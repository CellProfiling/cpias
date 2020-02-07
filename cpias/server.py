"""Provide an image analysis server."""
import asyncio
import concurrent.futures
import logging
from typing import Any, Callable, Coroutine, Dict, Optional

from .commands import get_commands
from .const import API_VERSION, LOGGER, VERSION
from .message import Message


class CPIAServer:
    """Represent an image analysis server."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, host: str = "localhost", port: int = 8555) -> None:
        """Set up server instance."""
        self.host = host
        self.port = port
        self.server: Optional[asyncio.AbstractServer] = None
        self.serv_task: Optional[asyncio.Task] = None
        self.commands: Dict[str, Callable] = {}
        self._on_stop_callbacks: list = []
        self._pending_tasks: list = []
        self._track_tasks = False
        self.store: dict = {}

    async def start(self) -> None:
        """Start server."""
        LOGGER.debug("Starting server")
        commands = get_commands()
        for module in commands.values():
            module.register_command(self)  # type: ignore

        server = await asyncio.start_server(
            self.handle_conn, host=self.host, port=self.port
        )
        self.server = server

        async with server:
            self.serv_task = asyncio.create_task(server.serve_forever())
            LOGGER.info("Serving at %s:%s", self.host, self.port)
            await self.serv_task

    async def stop(self) -> None:
        """Stop the server."""
        LOGGER.info("Server shutting down")
        self._track_tasks = True
        for stop_callback in self._on_stop_callbacks:
            stop_callback()

        self._on_stop_callbacks.clear()
        await self.wait_for_tasks()

        if self.serv_task is not None:
            self.serv_task.cancel()
            await asyncio.sleep(0)  # Let the event loop cancel the task.

    def on_stop(self, callback: Callable) -> None:
        """Register a callback that should be called on server stop."""
        self._on_stop_callbacks.append(callback)

    async def handle_conn(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle a connection."""
        # Send server version and server api version as welcome message.
        version_msg = f"CPIAServer version: {VERSION}, api version: {API_VERSION}\n"
        writer.write(version_msg.encode())
        await writer.drain()

        await self.handle_comm(reader, writer)

        LOGGER.debug("Closing the connection")
        writer.close()
        await writer.wait_closed()

    async def handle_comm(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle communication between client and server."""
        addr = writer.get_extra_info("peername")
        while True:
            data = await reader.readline()
            if not data:
                break
            msg = Message.decode(data.decode())
            if not msg:
                # TODO: Send invalid message message.  # pylint: disable=fixme
                continue

            cmd_func = self.commands.get(msg.command)

            if cmd_func is None:
                LOGGER.warning("Received unknown command %s from %s", msg.command, addr)
                # TODO: Send unknown command message.  # pylint: disable=fixme
                continue

            LOGGER.debug("Received %s from %s", msg, addr)
            LOGGER.debug("Executing command %s", msg.command)

            reply = await cmd_func(self, msg, **msg.data)

            LOGGER.debug("Sending: %s", reply)
            data = reply.encode().encode()
            writer.write(data)
            await writer.drain()

    def add_executor_job(self, func: Callable, *args: Any) -> Coroutine:
        """Schedule a function to be run in the thread pool.

        Return a task.
        """
        loop = asyncio.get_running_loop()
        task = loop.run_in_executor(None, func, *args)
        if self._track_tasks:
            self._pending_tasks.append(task)

        return task

    async def run_process_job(self, func: Callable, *args: Any) -> Any:
        """Run a job in the process pool."""
        loop = asyncio.get_running_loop()

        with concurrent.futures.ProcessPoolExecutor() as pool:
            task = loop.run_in_executor(pool, func, *args)
            if self._track_tasks:
                self._pending_tasks.append(task)
            result = await task

        return result

    def create_task(self, coro: Coroutine) -> asyncio.Task:
        """Schedule a coroutine on the event loop.

        Use this helper to make sure the task is cancelled on server stop.
        Return a task.
        """
        task = asyncio.create_task(coro)

        if self._track_tasks:
            self._pending_tasks.append(task)

        return task

    async def wait_for_tasks(self) -> None:
        """Wait for all pending tasks."""
        await asyncio.sleep(0)
        while self._pending_tasks:
            LOGGER.debug("Waiting for pending tasks")
            pending = [task for task in self._pending_tasks if not task.done()]
            self._pending_tasks.clear()
            if pending:
                await asyncio.wait(pending)
            else:
                await asyncio.sleep(0)


def main() -> None:
    """Run server."""
    logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")
    server = CPIAServer()
    try:
        asyncio.run(server.start(), debug=True)
    except KeyboardInterrupt:
        asyncio.run(server.stop(), debug=True)


if __name__ == "__main__":
    main()
