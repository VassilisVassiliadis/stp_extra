# Copyright IBM Inc. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Author: Vassilis Vassiliadis

from experiment.cli.configuration import Configuration
import stp_commands.exp

import typer
from rich.console import Console

stderr = Console(stderr=True)
stdout = Console()


app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    rich_markup_mode="rich",
    help="stp simplifies interactions with the Simulation Toolkit for Scientific Discovery (ST4SD)",
)


@app.callback()
def common_options(
    ctx: typer.Context,
):
    ctx.obj = Configuration(None, None, False)


app.add_typer(
    stp_commands.exp.app, name="experiment", help="List, describe, run experiments"
)


if __name__ == "__main__":
    app()
