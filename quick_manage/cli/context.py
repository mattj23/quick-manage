"""
    The context related commands
"""

import click
from ..environment import Environment, echo_line, echo_json


@click.group(name="context", invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context):
    env = Environment.default()

    echo_line(env.head("Contexts:"))
    for item in env.config.contexts:
        if env.config.active_context == item.name:
            echo_line(env.visible(f" > {item.name} ({item.type})"))
        else:
            echo_line(f"   {item.name} ({item.type})")

    echo_line()



