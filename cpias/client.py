"""Provide a test client for the CPIAServer."""
import asyncio

from cpias.const import LOGGER


async def tcp_client(message: str, host: str = "127.0.0.1", port: int = 8555) -> None:
    """Connect to server and send message."""
    reader, writer = await asyncio.open_connection(host, port)
    data = await reader.readline()
    version_msg = data.decode()
    LOGGER.debug("Version message: %s", version_msg.strip())

    LOGGER.info("Send: %r", message)
    writer.write(message.encode())
    await writer.drain()

    data = await reader.readline()
    LOGGER.info("Received: %r", data.decode())

    LOGGER.debug("Closing the connection")
    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(
        tcp_client('{"cli": "client-1", "cmd": "hello", "dta": {"planet": "world"}}\n'),
        debug=True,
    )
    asyncio.run(
        tcp_client(
            '{"cli": "client-1", "cmd": "hello_slow", "dta": {"planet": "slow"}}\n'
        ),
        debug=True,
    )
    asyncio.run(
        tcp_client(
            '{"cli": "client-1", "cmd": "hello_persistent", '
            '"dta": {"planet": "Mars"}}\n'
        ),
        debug=True,
    )
    asyncio.run(
        tcp_client(
            '{"cli": "client-1", "cmd": "hello_process", '
            '"dta": {"planet": "Neptune"}}\n'
        ),
        debug=True,
    )
