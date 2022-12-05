import click
from click import Context

from quick_manage.environment import Environment, echo_line
from quick_manage.ssh.client import SSHClient
from quick_manage.cli.common import HostNameType, StoreVarType, KeyNameType


@click.command(name="ssh")
@click.argument("host", type=HostNameType())
@click.argument("command", type=str)
@click.pass_context
def main(ctx: Context, host: str, command: str):
    env = Environment.default()
    host = env.get_host(host)
    client: SSHClient = host.get_client("ssh")
    conn = client.connect()
    conn.run(command)





