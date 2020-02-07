# type: ignore
"""Provide a CLI."""
import logging

import click

from cpias import __version__
from cpias.cli.client import run_client
from cpias.cli.server import start_server

SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(
    options_metavar="", subcommand_metavar="<command>", context_settings=SETTINGS
)
@click.option("--debug", is_flag=True, help="Start server in debug mode.")
@click.version_option(__version__)
@click.pass_context
def cli(ctx, debug):
    """Run CPIAS server."""
    ctx.obj = {}
    ctx.obj["debug"] = debug
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


cli.add_command(start_server)
cli.add_command(run_client)
