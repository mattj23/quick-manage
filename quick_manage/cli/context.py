"""
    The context related commands
"""
from typing import List

import click
from click import ParamType, Parameter
from click.shell_completion import CompletionItem

from ..environment import Environment, echo_line, echo_json


@click.group(name="context")
@click.pass_context
def main(ctx: click.Context):
    pass


@main.command(name="list")
@click.pass_context
def list_contexts(ctx: click.Context):
    """ List all available contexts in the configuration """
    env = Environment.default()

    echo_line(env.head("Contexts:"))
    for item in env.config.contexts:
        if env.config.active_context == item.name:
            echo_line(env.visible(f" > {item.name} ({item.type})"))
        else:
            echo_line(f"   {item.name} ({item.type})")

    echo_line()


class ContextNameType(ParamType):
    name = "context-name"

    def shell_complete(self, ctx: click.Context, param: Parameter, incomplete: str) -> List[CompletionItem]:
        env = Environment.default()
        return [CompletionItem(x.name) for x in env.config.contexts if x.name.startswith(incomplete)]


@main.command(name="set")
@click.pass_context
@click.argument("name", type=ContextNameType())
def set_context(ctx: click.Context, name: str):
    """ Set one of the available contexts to be the active focus """
    env = Environment.default()
    echo_line(f"Setting context to {name}")
