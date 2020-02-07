"""Provide process tools."""
import asyncio
import signal
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from time import sleep
from typing import TYPE_CHECKING, Any, Callable, Dict, Tuple

from cpias.const import LOGGER
from cpias.exceptions import CPIASError

if TYPE_CHECKING:
    from cpias.server import CPIAServer


class ReceiveError(CPIASError):
    """Error raised when receving from a process failed."""


def create_process(
    server: "CPIAServer", create_callback: Callable, *args: Any
) -> Tuple[Callable, Callable]:
    """Create a persistent process."""
    parent_conn, child_conn = Pipe()
    prc = Process(target=func_wrapper, args=(create_callback, child_conn, *args))
    prc.start()

    def stop_process() -> None:
        """Stop process."""
        prc.terminate()

    server.on_stop(stop_process)

    async def async_recv() -> Any:
        """Receive data from the process connection asynchronously."""
        while True:
            if not prc.is_alive() or parent_conn.poll():
                break
            await asyncio.sleep(0.5)

        if not prc.is_alive():
            raise ReceiveError
        try:
            return await server.add_executor_job(parent_conn.recv)
        except EOFError as exc:
            LOGGER.debug("Nothing more to receive")
            raise ReceiveError from exc

    async def async_send(data: Dict[Any, Any]) -> None:
        """Send data to the process."""
        parent_conn.send(data)

    return async_recv, async_send


def func_wrapper(create_callback: Callable, conn: Connection, *args: Any) -> None:
    """Wrap a function with connection to receive and send data."""
    running = True

    # pylint: disable=unused-argument
    def handle_signal(signum: int, frame: Any) -> None:
        """Handle signal."""
        nonlocal running
        running = False
        conn.close()

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    try:
        callback = create_callback(*args)
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.error("Failed to create callback: %s", exc)
        return

    while running:

        while running:
            if conn.poll():
                break
            sleep(0.5)

        try:
            data = conn.recv()
        except EOFError:
            LOGGER.debug("Nothing more to receive")
            break
        except OSError:
            LOGGER.debug("Connection is closed")
            break
        try:
            result = callback(data)
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.error("Failed to run callback: %s", exc)
            break

        if not running:
            break
        try:
            conn.send(result)
        except ValueError:
            LOGGER.error("Failed to send result %s", result)
        except OSError:
            LOGGER.debug("Connection is closed")
            break

    LOGGER.debug("Exiting process")
