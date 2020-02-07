# type: ignore
"""Provide a CLI to start the server."""
import asyncio

import click

from cpias.cli.common import common_tcp_options
from cpias.server import CPIAServer


@click.command(options_metavar="<options>")
@common_tcp_options
@click.pass_context
def start_server(ctx, host, port):
    """Start an async tcp server."""
    debug = ctx.obj["debug"]
    server = CPIAServer(host=host, port=port)
    try:
        asyncio.run(server.start(), debug=debug)
    except KeyboardInterrupt:
        asyncio.run(server.stop(), debug=debug)
