import sys
import typing as t
from typing import List, Dict

import click
from click import Context, Command

from quick_manage.cli.common import StoreVarType, SecretPathType, SecretPath, KeyPathType
from quick_manage.environment import Environment, echo_line, echo_json, echo_table
from quick_manage.keys import Secret, python_variable_name, IKeyCreateCommand, IKeyStore


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
        all_key_stores = list(env.active_context.key_stores.items())
        all_key_stores.sort(key=lambda ks: ks[0])
        echo_line(env.head(f"Key stores in context ({env.config.active_context}):"))
        for name, key_store in all_key_stores:
            key_store: IKeyStore
            echo_line(f"   {name} ({key_store.type_name})")


@main.command(name="list")
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
@click.option("-p", "--prefix", "secret_prefix", type=SecretPathType(), default=None,
              help="A prefix used to exclude secrets which don't match")
@click.pass_context
def list_all(ctx: click.Context, json_output, secret_prefix):
    """ Lists secrets in the active context with an optional prefix filter. """
    env = Environment.default()

    prefix = SecretPath.from_text(secret_prefix if secret_prefix else "")

    working = []

    if prefix.secret:
        # Already have the completed store name and some part of the path
        key_store = env.active_context.key_stores.get(prefix.store, None)
        if key_store:
            for s in key_store.all().values():
                if s.name.startswith(prefix.secret):
                    working.append((prefix.store, s))
    else:
        candidate_stores = [(k, v) for k, v in env.active_context.key_stores.items() if k.startswith(prefix.store)]
        for store_name, key_store in candidate_stores:
            for s in key_store.all().values():
                working.append((store_name, s))

    if json_output:
        collected = [{"store": n, "secret": s.name, "type": s.get_type_name()} for n, s in working]
        echo_json(collected)
        return

    list_of_rows = []
    for name, secret in working:
        list_of_rows.append([name, secret.name, f"{secret.get_type_name()}", f"{len(secret.get_keys())} keys"])
    list_of_rows.sort()
    list_of_rows = [["Store", "Secret", "Type", "Key Count"]] + list_of_rows
    echo_table(list_of_rows, header=env.head, spacing=3)


@main.command(name="put")
@click.argument("key_path", type=KeyPathType())
@click.argument("file", type=click.File('r'), default=sys.stdin)
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
@click.pass_context
def put(ctx: click.Context, key_path: str, file, json_output):
    """ Put a value for a secret/key into a store. The key contents may be specified as a file name or by redirection
    from stdin

    \b
    Examples:
        quick key put store_name/secret_name this_file.pem
        quick key put store_name/secret_name < /path/to/other/file
        curl https://key.example.com/value.txt | quick key put store_name/key_name
    """
    data = file.read()
    env = Environment.default()

    path = SecretPath.from_text(key_path)
    if not path.secret:
        echo_line(env.fail("No path was specified"))
        return

    try:
        key_store = env.active_context.key_stores.get(path.store, None)
        if not key_store:
            echo_line(env.fail(f"No key store named '{path.store}' was found in the active context"))
            return

        key_store.put_value(path.secret, path.key, data)
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
    """ Retrieves the information and metadata associated with a secret. """
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
@click.argument("key_path", type=KeyPathType())
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
@click.pass_context
def get(ctx: click.core.Context, key_path: str, json_output: bool):
    """ Writes the contents of a secret/key to stdout. """
    env = Environment.default()

    path = SecretPath.from_text(key_path)
    if not path.secret:
        echo_line(env.fail("No path was specified"))
        return
    try:
        key_store = env.active_context.key_stores.get(path.store, None)
        if not key_store:
            echo_line(env.fail(f"No key store named '{path.store}' was found in the active context"))
            return

        value = key_store.get_value(path.secret, path.key)
        if json_output:
            echo_json({"name": path.secret, "key": path.key, "value": value})
        else:
            echo_line(value)

    except KeyError as e:
        echo_line(env.fail(e), err=True)
    env = Environment.default()


@main.command(name="rm")
@click.argument("key_path", type=KeyPathType())
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
@click.option("-y", "--yes", "confirm_delete", is_flag=True, help="Confirm deletion non-interactively")
@click.pass_context
def remove(ctx: click.Context, key_path: str, json_output: bool, confirm_delete: bool):
    """ Deletes a secret or key from the specified store (see options). """
    env = Environment.default()

    if not confirm_delete and not click.confirm("Are you sure you want to remove this key?"):
        return

    path = SecretPath.from_text(key_path)
    if not path.secret:
        echo_line(env.fail("No path was specified"))
        return
    try:
        key_store = env.active_context.key_stores.get(path.store, None)
        if not key_store:
            echo_line(env.fail(f"No key store named '{path.store}' was found in the active context"))
            return

        key_store.rm(path.secret, path.key)
        if json_output:
            echo_json({"name": path.secret, "key": path.key})
        else:
            echo_line(f"Key '{path.secret}@{path.key}' deleted from '{path.store}'")

    except KeyError as e:
        echo_line(env.fail(e), err=True)


def _secret_type(type_name: str, environ: Environment):
    def create_function(**kwargs):
        secret_type = next(s for s in environ.secret_types if s.name == type_name)
        expected_keys = {sk: python_variable_name(sk) for sk in secret_type.keys}

        found_keys = {}
        for key, option_name in expected_keys.items():
            file = kwargs.get(option_name, None)
            if file is not None:
                found_keys[key] = file.read()

        secret_path = kwargs["secret_path"]
        path = SecretPath.from_text(secret_path)
        if not path.secret:
            echo_line(environ.fail("No path was specified"))
            return

        try:
            key_store = environ.active_context.key_stores.get(path.store, None)
            if not key_store:
                echo_line(environ.fail(f"No key store named '{path.store}' was found in the active context"))
                return

            if key_store.has_secret(path.secret):
                echo_line(environ.fail(f"A secret already exists at '{path.secret}'"))
                return

            for key_name, data in found_keys.items():
                key_store.put_value(path.secret, key_name, data)
            key_store.set_meta(path.secret, {"type": type_name})

            echo_line(f"Stored value to secret '{path.secret}' in store '{path.store}'")
        except KeyError as e:
            echo_line(environ.fail(e), err=True)

    return create_function


def _create_command(creator: IKeyCreateCommand, environ: Environment):
    def create_function(**kwargs):
        path = SecretPath.from_text(kwargs["secret_path"])
        overwrite = kwargs["overwrite"]
        if not path.secret:
            echo_line(environ.fail("No path was specified"))
            return

        try:
            key_store = environ.active_context.key_stores.get(path.store, None)
            if not key_store:
                echo_line(environ.fail(f"No key store named '{path.store}' was found in the active context"))
                return

            sub_kwargs = {k: kwargs[k] for k in kwargs.keys() if k not in {"secret_path", "overwrite"}}
            try:
                key_values = creator.on_create(**sub_kwargs)
            except ValueError as e:
                echo_line(environ.fail(str(e)), err=True)
                return

            if key_store.has_secret(path.secret):
                if not overwrite:
                    echo_line(environ.fail(f"A secret already exists at '{path.secret}' "
                                           f"(did you mean to use -o/--overwrite?)"), err=True)
                    return
                else:
                    secret = key_store.get_meta(path.secret)
                    for sub_key in secret.keys:
                        print(f"rm {path.secret}@{sub_key}")
                        key_store.rm(path.secret, sub_key)

            sub_kwargs = {k: kwargs[k] for k in kwargs.keys() if k not in {"secret_path", "overwrite"}}
            for key_name, data in creator.on_create(**sub_kwargs).items():
                key_store.put_value(path.secret, key_name, data)
            key_store.set_meta(path.secret, {"type": creator.secret_type_name})

            echo_line(f"Stored value to secret '{path.secret}' in store '{path.store}'")
        except KeyError as e:
            echo_line(environ.fail(e), err=True)

    return create_function


class CreateMultiCommand(click.MultiCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.env = Environment.default()

        # TODO: these can probably be unified
        self.secret_types = {x.name: x for x in self.env.secret_types}
        self.creators = {x.name: x for x in self.env.key_creators}
        self.command_names = list(set(self.secret_types.keys()).union(set(self.creators.keys())))
        self.command_names.sort()

    def list_commands(self, ctx: Context) -> t.List[str]:
        return self.command_names

    def get_command(self, ctx: Context, cmd_name: str) -> t.Optional[Command]:
        if cmd_name in self.secret_types:
            cmd = Command(name=cmd_name, callback=_secret_type(cmd_name, self.env), help=f"{cmd_name} help")
            cmd.params.append(click.Argument(["secret_path"], type=SecretPathType()))
            for sk in self.secret_types[cmd_name].keys:
                option = click.Option([f"--{sk}", python_variable_name(sk)],
                                      default=None, help=f"Set a file for the '{sk}' key in the secret",
                                      type=click.File('r'))
                cmd.params.append(option)
            return cmd

        elif cmd_name in self.creators:
            creator: IKeyCreateCommand = self.creators[cmd_name]
            cmd = Command(name=cmd_name, callback=_create_command(creator, self.env), help=creator.help)
            cmd.params.append(click.Argument(["secret_path"], type=SecretPathType()))
            cmd.params.append(click.Option(["-o", "--overwrite", "overwrite"], is_flag=True,
                                           help="Overwrite an existing secret with the same name"))
            creator.configure_command(cmd)
            return cmd

        else:
            raise NotImplementedError(f"No implementation for {cmd_name}")


@main.group(name="create", cls=CreateMultiCommand)
@click.pass_context
def create(ctx: click.Context):
    """ Create a secret from a known type. """
    pass
