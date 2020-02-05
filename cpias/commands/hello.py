"""Provide the hello command."""
from typing import TYPE_CHECKING, Optional

from cpias.const import LOGGER
from cpias.message import Message

from . import validate

if TYPE_CHECKING:
    from cpias.server import CPIAServer

# pylint: disable=unused-argument


def register_command(server: "CPIAServer") -> None:
    """Register the hello command."""
    server.commands["hello"] = hello


@validate({"planet": str})
async def hello(
    server: "CPIAServer", message: Message, planet: Optional[str] = None
) -> Message:
    """Run the hello command."""
    if planet is None:
        planet = "Jupiter"
    LOGGER.info("Hello %s!", planet)
    return message
