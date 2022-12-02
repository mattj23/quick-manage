import getpass
import click

from quick_manage.ssh.client import create_remote_admin


@click.group(name="host")
@click.pass_context
def host_command(ctx: click.core.Context):
    pass


@host_command.command(name="setup-admin")
@click.argument("username", type=str)
@click.argument("host", type=str)
@click.pass_context
def setup_admin(ctx: click.core.Context, username: str, host: str):
    """ Set up a remote_admin user on a remote ssh linux machine.

    This will create a user named "remote_admin" on the specified system with password-less sudo and no ability to
    login without an ssh key.
    """
    sudo_pass = getpass.getpass("Enter password for remote system: ")
    create_remote_admin(username, host, sudo_pass)
