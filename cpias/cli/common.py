# type: ignore
"""Provide common CLI options."""
import click


def common_tcp_options(func):
    """Supply common tcp connection options."""
    func = click.option(
        "-p",
        "--port",
        default=8555,
        show_default=True,
        type=int,
        help="TCP port of the connection.",
    )(func)
    func = click.option(
        "-H",
        "--host",
        default="127.0.0.1",
        show_default=True,
        help="TCP address of the server.",
    )(func)
    return func
