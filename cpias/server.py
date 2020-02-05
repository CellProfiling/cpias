"""Provide an image analysis server."""
import asyncio
import logging
from typing import Callable, Dict, Optional

from .commands import get_commands
from .const import API_VERSION, LOGGER, VERSION
from .message import Message


class CPIAServer:
    """Represent an image analysis server."""

    def __init__(self, host: str = "localhost", port: int = 8555) -> None:
        """Set up server instance."""
        self.host = host
        self.port = port
        self.server: Optional[asyncio.AbstractServer] = None
        self.serv_task: Optional[asyncio.Task] = None
        self.commands: Dict[str, Callable] = {}

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
            LOGGER.debug("Serving at %s:%s", self.host, self.port)
            await self.serv_task

    async def stop(self) -> None:
        """Stop the server."""
        if self.serv_task is not None:
            self.serv_task.cancel()
            await asyncio.sleep(0)  # Let the event loop cancel the task.

    async def handle_conn(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle a connection."""
        # Send server version and server api version as welcome message.
        version_msg = f"CPIAServer version: {VERSION}, api version: {API_VERSION}\n"
        writer.write(version_msg.encode())
        await writer.drain()

        await self.handle_comm(reader, writer)

        LOGGER.info("Closing the connection")
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
                # TODO: Send invalid message message.
                continue

            cmd_func = self.commands.get(msg.command)

            if cmd_func is None:
                LOGGER.warning("Received unknown command %s from %s", msg.command, addr)
                # TODO: Send unknown command message.
                continue

            LOGGER.debug("Received %s from %s", msg, addr)
            LOGGER.debug("Executing command %s", msg.command)

            reply = await cmd_func(self, msg, **msg.data)

            LOGGER.debug("Sending: %s", reply)
            data = reply.encode().encode()
            writer.write(data)
            await writer.drain()


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
