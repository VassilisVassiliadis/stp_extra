# Copyright IBM Inc. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Author: Vassilis Vassiliadis

import os.path
import typing

import experiment.service.db

import typer
from rich.console import Console

from experiment.cli.api import get_api

app = typer.Typer(no_args_is_help=True)

stderr = Console(stderr=True)
stdout = Console()


@app.command("list")
def cli_list_experiments(
    ctx: typer.Context,
):
    """
    List available experiments
    """
    api = get_api(ctx, for_context=None)

    experiments = api.api_experiment_list()

    entries = {}

    for entry, package in experiments.items():
        name, digest = entry.split("@")
        if name == "lammps":
            stdout.print(package)

        if name not in entries:
            entries[name] = {}

        for tags in package["metadata"]["registry"].get("tags", []):
            entries[name][tags] = name

    for name, info in entries.items():
        stdout.print(name)

        for tag in info:
            print("  ", ":".join((name, tag)))


@app.command(no_args_is_help=True)
def describe(
    ctx: typer.Context,
    identifier: str = typer.Argument(
        ..., help="The experiment identifier", show_default=False
    ),
):
    """Describes the required and optional configurations of an experiment
    """
    api = get_api(ctx, None)
    pvep = api.api_experiment_get(experiment_identifier=identifier)

    input_files = [x["name"] for x in pvep["metadata"]["registry"].get("inputs", [])]

    if input_files:
        stdout.print("Input files you must provide")
        for x in input_files:
            stdout.print("  ", x)

    if pvep["parameterisation"]["executionOptions"].get("variables", []):
        stdout.print("Parameters you may optionally override")

        for param in pvep["parameterisation"]["executionOptions"].get("variables", []):
            print("  ", param["name"])

            if "values" in param:
                print("    Available options")
                for value in param["values"]:
                    print("      ", value)
                print("    Default value:", param["values"][0])

            if "value" in param:
                print("    Default value:", param["value"])


def run(
    api: experiment.service.db.ExperimentRestAPI,
    identifier: str,
    inputs: typing.Dict[str, str],
    parameters: typing.Dict[str, typing.Union[str, int, float, bool]],
) -> str:
    payload = {"inputs": []}

    for name, path in inputs.items():
        with open(path, "r") as f:
            data = f.read()
        payload["inputs"].append({"filename": name, "content": data})

    payload["variables"] = {k: str(v) for k, v in parameters.items()}
    return api.api_experiment_start(identifier, payload)


@app.command(name="run", no_args_is_help=True)
def cli_run(
    ctx: typer.Context,
    identifier: str = typer.Argument(
        ..., help="The experiment identifier", show_default=False
    ),
    input: typing.List[str] = typer.Option(
        [],
        help="The input files to the experiment. You may rename them by "
        "prefixing them with the new name e.g. foo:/hello/world.txt will "
        "upload the file /hello/world.txt to the runtime service using the name foo",
    ),
    parameter: typing.List[str] = typer.Option(
        [],
        help="A key=value to override one of experiment parameters. May set this argument multiple times",
    ),
):
    """Runs an experiment
    """
    parsed_parameters = {}
    for p in parameter:
        name, value = p.split("=", 1)
        parsed_parameters[name] = value
    input_files = {}

    for i in input:
        if ":" in i:
            name, path = i.split(":", 1)
            input_files[name] = path
        else:
            input_files[os.path.basename(i)] = i

    api = get_api(ctx, for_context=None)

    rest_uid = run(
        api=api, identifier=identifier, inputs=input_files, parameters=parsed_parameters
    )
    stdout.print(f"[green]{rest_uid}[/green]")
