import sys

import click
from quick_manage.environment import Environment, echo_line, echo_json


@click.group(name="key")
@click.pass_context
def main(ctx: click.core.Context):
    pass


@main.group()
@click.pass_context
def store(ctx: click.core.Context):
    pass


@main.command(name="list")
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
@click.pass_context
def list_all(ctx: click.core.Context, json_output):
    env: Environment = ctx.obj
    all_items = env.list_keys()

    if json_output:
        echo_json(all_items)
        return

    for name, results in all_items.items():
        if results["default"]:
            echo_line(env.visible(f"{name} (default):"))
        else:
            echo_line(f"{name}:")

        if results['error']:
            echo_line(env.fail(f" * error getting keys: {results['error']}"))
            continue

        if results['keys']:
            for item in results['keys']:
                echo_line(" > ", item)
        else:
            echo_line(" * No stored keys")


@main.command(name="put")
@click.argument("name", type=str)
@click.argument("file", type=click.File('r'), default=sys.stdin)
@click.option("-s", "--store", "store_name", type=str, help="Specify the store, otherwise the default will be used")
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
@click.pass_context
def put(ctx: click.core.Context, name: str, file, store_name, json_output):
    """ Put a key in a store. The key contents may be specified as a file name or by redirection from stdin

    \b
    Examples:
        quick key put key_name this_file.pem
        quick key put key_name < /path/to/other/file
        curl https://key.example.com/value.txt | quick key put key_name
    """
    data = file.read()
    env: Environment = ctx.obj

    try:
        env.put_key(name, data, store_name)
        if json_output:
            echo_json({"name": name, "value": data, "store": store_name})
        else:
            echo_line(f"Stored value to key '{name}' in store '{store_name}'")
    except KeyError as e:
        echo_line(env.fail(e), err=True)


@main.command(name="get")
@click.argument("name", type=str)
@click.option("-s", "--store", "store_name", type=str, help="Specify the store, otherwise the default will be used",
              default=None)
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
@click.pass_context
def get(ctx: click.core.Context, name: str, store_name: str, json_output: bool):
    """ Writes the contents of a key to stdout """
    env: Environment = ctx.obj
    try:
        data = env.get_key(name, store_name)
        if json_output:
            echo_line(json.dumps({"name": name, "value": data}))
        else:
            echo_line(data)
    except KeyError as e:
        echo_line(env.fail(e), err=True)
