from experiment.cli.configuration import Configuration
import stp_commands.exp

from typing import Optional
from pathlib import Path
import typer
from rich.console import Console
import experiment.cli.api

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
    settings_file: Optional[Path] = typer.Option(
        None,
        help=f"Path to the {experiment.cli.configuration.DEFAULT_SETTINGS_FILE_NAME} file",
        envvar="STP_SETTINGS_FILE",
        exists=True,
        readable=True,
        resolve_path=True,
        show_default=False,
    ),
    contexts_file: Optional[Path] = typer.Option(
        None,
        help=f"Path to the {experiment.cli.configuration.DEFAULT_CONTEXTS_FILE_NAME} file",
        envvar="STP_CONTEXTS_FILE",
        exists=True,
        readable=True,
        resolve_path=True,
        show_default=False,
    ),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Use verbose output"),
):
    # Use the context to store the configuration
    ctx.obj = Configuration(settings_file, contexts_file, verbose)


# Add subcommands from different file
app.add_typer(
    stp_commands.exp.app, name="experiment", help="List, decribe, run experiments"
)


if __name__ == "__main__":
    app()
