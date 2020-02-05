"""Provide a model for messages sent and received by the server."""
from __future__ import annotations

import json
from enum import Enum
from typing import Optional

from .const import LOGGER


class Message:
    """Represent a client/server message."""

    def __init__(self, *, client: str, command: str, data: dict) -> None:
        """Set up message instance."""
        self.client = client
        self.command = command
        self.data = data

    def __repr__(self) -> str:
        """Return the representation."""
        return (
            f"{type(self).__name__}(client={self.client}, command={self.command}, "
            f"data={self.data})"
        )

    @classmethod
    def decode(cls, data: str) -> Optional[Message]:
        """Decode data into a message."""
        # '{"cli": "client-1", "cmd": "hello", "dta": {"param1": "world"}}'
        try:
            parsed_data = json.loads(data.strip())
        except ValueError:
            LOGGER.error("Failed to parse message data: %s", data)
            return None
        if not isinstance(parsed_data, dict):
            LOGGER.error("Incorrect message data: %s", parsed_data)
            return None
        params: dict = {
            block.name: parsed_data.get(block.value) for block in MessageBlock
        }
        return cls(**params)

    def encode(self) -> str:
        """Encode message into a data string."""
        compiled_msg = {attr.value: getattr(self, attr.name) for attr in MessageBlock}
        return f"{json.dumps(compiled_msg)}\n"


class MessageBlock(Enum):
    """Represent a message block."""

    client = "cli"
    command = "cmd"
    data = "dta"
