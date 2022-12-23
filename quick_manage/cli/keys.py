import sys
from typing import List, Dict

import click
from quick_manage.cli.common import StoreVarType, KeyNameType, SecretPathType, SecretPath
from quick_manage.environment import Environment, echo_line, echo_json
from quick_manage.keys import Secret


@click.group(name="key")
@click.pass_context
def main(ctx: click.core.Context):
    pass


@main.group(name="store", invoke_without_command=True)
@click.pass_context
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
def store(ctx: click.Context, json_output):
    """ List all key stores """
    env = Environment.default()

    if json_output:
        pass
    else:
        all_key_stores = list(env.active_context.key_stores.keys())
        echo_line(env.head(f"Key stores in context ({env.config.active_context}):"))
        for key_store in all_key_stores:
            echo_line(f"   {key_store}")


@main.command(name="list")
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
@click.option("-s", "--store", "store_name", type=StoreVarType(), default=None,
              help="Specify the store, otherwise the default will be used")
@click.pass_context
def list_all(ctx: click.core.Context, json_output, store_name):
    env = Environment.default()
    all_items = env.list_keys(store_name)

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
@click.argument("secret_path", type=SecretPathType())
@click.argument("file", type=click.File('r'), default=sys.stdin)
@click.option("-k", "--key", "key_name", type=KeyNameType(), default=None)
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
@click.pass_context
def put(ctx: click.Context, secret_path: str, file, json_output, key_name):
    """ Put a key in a store. The key contents may be specified as a file name or by redirection from stdin

    \b
    Examples:
        quick key put store_name/secret_name this_file.pem
        quick key put store_name/secret_name < /path/to/other/file
        curl https://key.example.com/value.txt | quick key put store_name/key_name
    """
    data = file.read()
    env = Environment.default()

    path = SecretPath.from_text(secret_path)
    if not path.secret:
        echo_line(env.fail("No path was specified"))
        return

    try:
        key_store = env.active_context.key_stores.get(path.store, None)
        if not key_store:
            echo_line(env.fail(f"No key store named '{path.store}' was found in the active context"))
            return

        key_store.put_value(path.secret, None, data)
        if json_output:
            echo_json({"name": path.secret, "value": data, "store": path.store})
        else:
            echo_line(f"Stored value to secret '{path.secret}' in store '{path.store}'")
    except KeyError as e:
        echo_line(env.fail(e), err=True)


@main.command(name="info")
@click.argument("secret_path", type=SecretPathType())
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
@click.pass_context
def info(ctx: click.Context, secret_path: str, json_output: bool):
    """ Writes the contents of a key to stdout """
    env = Environment.default()

    path = SecretPath.from_text(secret_path)
    if not path.secret:
        echo_line(env.fail("No path was specified"))
        return
    try:
        key_store = env.active_context.key_stores.get(path.store, None)
        if not key_store:
            echo_line(env.fail(f"No key store named '{path.store}' was found in the active context"))
            return

        meta_data: Secret = key_store.get_meta(path.secret)
        key_names = list(meta_data.keys.keys()) if meta_data.keys else []
        meta_info: Dict = meta_data.meta_data if meta_data.meta_data else {}
        if json_output:
            echo_json({"name": path.secret, "store": path.store, "meta_data": meta_info, "keys": key_names})
        else:
            echo_line(env.head(f"Secret {secret_path}:"))
            if key_names:
                echo_line("Keys:")
                for k in sorted(key_names):
                    echo_line(f" * {k}")
            else:
                echo_line("Keys: ", env.warning("(none)"))

            if meta_info.items():
                echo_line("Metadata:")
                for k, v in meta_info.items():
                    echo_line(f" * {k}: {v}")
            else:
                echo_line("Metadata: ", env.warning("(none)"))


    except KeyError as e:
        echo_line(env.fail(e), err=True)


@main.command(name="get")
@click.argument("name", type=KeyNameType())
@click.option("-s", "--store", "store_name", type=StoreVarType(), default=None,
              help="Specify the store, otherwise the default will be used")
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
@click.pass_context
def get(ctx: click.core.Context, name: str, store_name: str, json_output: bool):
    """ Writes the contents of a key to stdout """
    env = Environment.default()
    try:
        data = env.get_key(name, store_name)
        if json_output:
            echo_json({"name": name, "value": data})
        else:
            echo_line(data)
    except KeyError as e:
        echo_line(env.fail(e), err=True)


@main.command(name="rm")
@click.argument("name", type=KeyNameType())
@click.option("-s", "--store", "store_name", type=StoreVarType(), help="Specify the store")
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
@click.option("-y", "--yes", "confirm_delete", is_flag=True, help="Confirm deletion non-interactively")
@click.pass_context
def remove(ctx: click.core.Context, name: str, store_name: str, json_output: bool, confirm_delete: bool):
    """ Deletes a key from the specified store """
    env = Environment.default()
    if not store_name:
        echo_line(env.fail("Must specify a store name to remove a key"), err=True)
        return

    if not confirm_delete and not click.confirm("Are you sure you want to remove this key?"):
        return

    try:
        env.rm_key(name, store_name)
        if json_output:
            echo_json({"name": name, "store": store_name})
        else:
            echo_line(f"Key '{name}' deleted from '{store_name}'")
    except KeyError as e:
        echo_line(env.fail(e), err=True)
