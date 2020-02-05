"""Provide commands to the server."""
from functools import wraps
from types import ModuleType
from typing import Callable, Mapping

import pkg_resources
import voluptuous as vol
from voluptuous.humanize import humanize_error

from cpias.const import LOGGER
from cpias.message import Message


def get_commands() -> Mapping[str, ModuleType]:
    """Return a dict of command modules."""
    commands = {
        entry_point.name: entry_point.load()
        for entry_point in pkg_resources.iter_entry_points("cpias.commands")
    }
    return commands


def validate(schema: dict) -> Callable:
    """Return a decorator for argument validation."""

    vol_schema = vol.Schema(schema)

    def decorator(func: Callable) -> Callable:
        """Decorate a function and validate its arguments."""

        @wraps(func)
        async def check_args(server, message, **data):  # type: ignore
            """Check arguments."""
            try:
                data = vol_schema(data)
            except vol.Invalid as exc:
                err = humanize_error(data, exc)
                LOGGER.error(
                    "Received invalid data for command %s: %s", message.command, err
                )
                return Message(client=message.client, command="invalid", data=data)

            return await func(server, message, **data)

        return check_args

    return decorator
