"""Provide tests for message."""
from cpias.message import Message


def test_message_decode():
    """Test message decode."""
    msg = Message.decode(
        '{"cli": "client-1", "cmd": "hello", "dta": {"param1": "world"}}'
    )

    assert msg.client == "client-1"
    assert msg.command == "hello"
    assert msg.data == {"param1": "world"}


def test_decode_bad_message():
    """Test decode bad message."""
    msg = Message.decode("bad")

    assert not msg

    msg = Message.decode('["val1", "val2"]')

    assert not msg


def test_message_encode():
    """Test message encode."""
    msg_string = '{"cli": "client-1", "cmd": "hello", "dta": {"param1": "world"}}\n'
    msg = Message.decode(msg_string)

    msg_encoded = msg.encode()

    assert msg_encoded == msg_string
