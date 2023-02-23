import getpass
import click

from quick_manage.environment import Environment, echo_line, echo_json
from quick_manage.ssh.client import create_remote_admin, SSHClient
from quick_manage.ssh.keys import generate_key_pair, private_key_from_string
from quick_manage.cli.common import HostNameType, StoreVarType, KeyPathType


@click.group(name="host")
@click.pass_context
def host_command(ctx: click.Context):
    pass


@host_command.command(name="ls")
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
@click.pass_context
def list_command(ctx: click.Context, json_output):
    env = Environment.default()
    names = sorted(env.active_context.host_names)
    if json_output:
        echo_json(names)
    else:
        echo_line(env.head("Hosts"))
        if not names:
            echo_line(env.warning("  (none)"))
        else:
            for name in names:
                echo_line(f"  {name}")


@host_command.command(name="test")
@click.argument("host-name", type=HostNameType())
@click.pass_context
def list_command(ctx: click.Context, host_name):
    env = Environment.default()
    host = env.active_context.hosts[host_name]

    client: SSHClient = host.get_client_by_type("ssh")
    connection = client.connect()
    print(connection.run("whoami"))



@host_command.command(name="ssh")
@click.argument("host", type=HostNameType())
@click.argument("command", type=str)
@click.pass_context
def ssh_command(ctx: click.Context, host: str, command: str):
    print(command)


@host_command.command(name="setup-admin")
@click.argument("host", type=HostNameType())
@click.argument("sudo-user", type=str)
@click.option("-n", "--name", "user_name", type=str, default="remote_admin",
              help="Name of the remote administrative user to create (default is remote_admin)")
@click.option("-k", "--key", "key_path", type=KeyPathType(), default=None,
              help="Specify the key name, otherwise one will be generated")
@click.pass_context
def setup_admin(ctx: click.Context, host: str, sudo_user: str, user_name: str, store_name, key_name):
    """ Set up a remote_admin user on a remote ssh linux machine using already existing sudo credentials.

    This will create a user (named "remote_admin" unless specified) on the selected host with password-less sudo and no
    ability to login without an ssh key.

    A key name and store may be specified.

    If a key name is specified, the system will attempt to find a key with that name either in the global scope (if no
    store is given) or in a specific store if one is provided. If no key with that name can be located, a new ED25519
    keypair will be created and saved with that name.

    If no key name is specified, one will be created using the admin name and the host name and saved in the specified
    store (or the default store if none was given)
    """
    env = Environment.default()

    if key_name is None:
        key_name = f"{user_name}-{host}.key"

    try:
        found_key = env.get_key(key_name, store_name)
    except KeyError:
        found_key = None

    if found_key:
        pkey, _ = private_key_from_string(found_key)
        public_key = pkey.get_name() + " " + pkey.get_base64()
    else:
        public_key, private_key = generate_key_pair()
        save_store = store_name if store_name else env.default_key_store
        env.put_key(key_name, private_key, save_store)

    # Modify the host configuration
    # TODO: make this better, don't add twice
    cfg_d = [x for x in env.config.hosts if x["host"] == host][0]
    if "client" not in cfg_d:
        cfg_d["client"] = []
    cfg_d["client"].append({"type": "ssh", "user": user_name, "key": key_name})
    env.config.write()

    sudo_pass = getpass.getpass("Enter password for remote system: ")
    create_remote_admin(sudo_user, host, sudo_pass, user_name, public_key)
