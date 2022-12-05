import getpass
import click

from quick_manage.environment import Environment, echo_line
from quick_manage.ssh.client import create_remote_admin
from quick_manage.ssh.keys import generate_key_pair, private_key_from_string
from quick_manage.cli.common import HostNameType, StoreVarType, KeyNameType


@click.group(name="host")
@click.pass_context
def host_command(ctx: click.core.Context):
    pass


@host_command.command(name="setup-admin")
@click.argument("host", type=HostNameType())
@click.argument("sudo-user", type=str)
@click.option("-n", "--name", "user_name", type=str, default="remote_admin",
              help="Name of the remote administrative user to create (default is remote_admin)")
@click.option("-s", "--store", "store_name", type=StoreVarType(), default=None,
              help="Specify the store, otherwise the default will be used")
@click.option("-k", "--key", "key_name", type=KeyNameType(), default=None,
              help="Specify the key name, otherwise one will be generated")
@click.pass_context
def setup_admin(ctx: click.core.Context, host: str, sudo_user: str, user_name: str, store_name, key_name):
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

    print(public_key)

    return
    echo_line(store_name)
    echo_line(key_name)

    sudo_pass = getpass.getpass("Enter password for remote system: ")
    create_remote_admin(sudo_user, host, sudo_pass, user_name)
