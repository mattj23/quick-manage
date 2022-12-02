import sys

import click
from quick_manage.environment import Environment, echo_line


@click.group(name="key")
@click.pass_context
def main(ctx: click.core.Context):
    pass


@main.group()
@click.pass_context
def store(ctx: click.core.Context):
    pass


@main.command(name="list")
@click.pass_context
def list_all(ctx: click.core.Context):
    env: Environment = ctx.obj
    all_keys = env.key_store.list()
    if all_keys:
        echo_line("Keys:")

        for item in env.key_store.list():
            echo_line(" > ", item)
    else:
        echo_line("[No stored keys]")


@main.command(name="put")
@click.argument("name", type=str)
@click.argument("file", type=click.File('r'), default=sys.stdin)
@click.pass_context
def put(ctx: click.core.Context, name: str, file):
    env: Environment = ctx.obj

    data = file.read()
    env.key_store.put(name, data)
    echo_line(f"Stored value to key '{name}'")


@main.command(name="get")
@click.argument("name", type=str)
@click.pass_context
def put(ctx: click.core.Context, name: str):
    env: Environment = ctx.obj

    try:
        data = env.key_store.get(name)
        echo_line(data)
    except KeyError as e:
        echo_line(env.config.styles.fail(e))
