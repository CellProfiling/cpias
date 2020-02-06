"""Provide the hello command."""
from typing import TYPE_CHECKING, Callable, Optional, Tuple

from cpias.commands import validate
from cpias.const import LOGGER
from cpias.message import Message
from cpias.process import ReceiveError, create_process

if TYPE_CHECKING:
    from cpias.server import CPIAServer

# pylint: disable=unused-argument


def register_command(server: "CPIAServer") -> None:
    """Register the hello command."""
    server.commands["hello"] = hello
    server.commands["hello_slow"] = hello_slow
    server.commands["hello_persistent"] = hello_persistent
    server.commands["hello_process"] = hello_process


@validate({"planet": str})
async def hello(
    server: "CPIAServer", message: Message, planet: Optional[str] = None
) -> Message:
    """Run the hello command."""
    if planet is None:
        planet = "Jupiter"
    LOGGER.info("Hello %s!", planet)
    return message


@validate({"planet": str})
async def hello_slow(
    server: "CPIAServer", message: Message, planet: Optional[str] = None
) -> Message:
    """Run the slow hello command."""
    if planet is None:
        planet = "Jupiter"

    result = await server.run_process_job(do_cpu_work)

    LOGGER.info("Hello %s! The result is %s", planet, result)

    reply = message.copy()
    reply.data["result"] = result

    return reply


@validate({"planet": str})
async def hello_persistent(
    server: "CPIAServer", message: Message, planet: Optional[str] = None
) -> Message:
    """Run the persistent hello command.

    This command creates a state the first time it's run.
    """
    if planet is None:
        planet = "Jupiter"

    if "hello_persistent_state" not in server.store:
        server.store["hello_persistent_state"] = create_state()

    command_task = server.store["hello_persistent_state"]

    old_planet, new_planet = command_task(planet)

    LOGGER.info(
        "Hello! The old planet was %s. The new planet is %s", old_planet, new_planet
    )

    reply = message.copy()
    reply.data["old_planet"] = old_planet
    reply.data["new_planet"] = new_planet

    return reply


@validate({"planet": str})
async def hello_process(
    server: "CPIAServer", message: Message, planet: Optional[str] = None
) -> Message:
    """Run the process hello command.

    This command creates a process the first time it's run.
    """
    if planet is None:
        planet = "Jupiter"

    if "hello_process" not in server.store:
        server.store["hello_process"] = create_process(server, create_state)

    recv, send = server.store["hello_process"]

    await send(planet)

    try:
        old_planet, new_planet = await recv()
    except ReceiveError:
        return message

    LOGGER.info(
        "Hello! The old planet was %s. The new planet is %s", old_planet, new_planet
    )

    reply = message.copy()
    reply.data["old_planet"] = old_planet
    reply.data["new_planet"] = new_planet

    return reply


def do_cpu_work() -> int:
    """Do work that should run in the process pool."""
    return sum(i * i for i in range(10 ** 7))


def create_state() -> Callable:
    """Initialize state."""

    state: str = "init"

    def change_state(new_state: str) -> Tuple[str, str]:
        """Do work that should change state."""
        nonlocal state
        old_state = state
        state = new_state

        return old_state, new_state

    return change_state
