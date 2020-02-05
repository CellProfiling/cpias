"""Provide a test client for the CPIAServer."""
import asyncio


async def tcp_echo_client(message: str) -> None:
    """Connect to server and send message."""
    reader, writer = await asyncio.open_connection("localhost", 8555)
    data = await reader.readline()
    version_msg = data.decode()
    print(f"Version message: {version_msg}")

    for _ in range(2):
        print(f"Send: {message!r}")
        writer.write(message.encode())
        await writer.drain()

        data = await reader.readline()
        print(f"Received: {data.decode()!r}")

        await asyncio.sleep(2)

    print("Closing the connection")
    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(
        tcp_echo_client(
            '{"cli": "client-1", "cmd": "hello", "dta": {"planet": "world"}}\n'
        ),
        debug=True,
    )
