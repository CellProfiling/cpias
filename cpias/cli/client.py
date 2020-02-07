# type: ignore
"""Provide a CLI to start a client."""
import asyncio

import click

from cpias.cli.common import common_tcp_options
from cpias.client import tcp_client

DEFAULT_MESSAGE = '{"cli": "client-1", "cmd": "hello", "dta": {"planet": "world"}}\n'


@click.command(options_metavar="<options>")
@click.option("--message", default=DEFAULT_MESSAGE, help="Message to send to server.")
@common_tcp_options
@click.pass_context
def run_client(ctx, message, host, port):
    """Run an async tcp client to connect to the server."""
    debug = ctx.obj["debug"]
    asyncio.run(
        tcp_client(message, host=host, port=port), debug=debug,
    )
