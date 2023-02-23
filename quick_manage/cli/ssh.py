import os
from contextlib import contextmanager
from typing import List
import subprocess

import click
from click import Context

from quick_manage.environment import Environment, echo_line
from quick_manage.ssh.client import SSHClient
from quick_manage.cli.common import HostNameType, StoreVarType

from tempfile import NamedTemporaryFile


@contextmanager
def temp_key_file():
    temp_file = NamedTemporaryFile(mode="w", delete=False)
    try:
        yield temp_file
    finally:
        temp_file.close()
        os.remove(temp_file.name)


@click.command(name="ssh")
@click.argument("host-name", type=HostNameType())
@click.argument("commands", nargs=-1)
@click.pass_context
def main(ctx: Context, host_name: str, commands: List[str]):
    env = Environment.default()
    host = env.active_context.hosts[host_name]

    if commands:
        client: SSHClient = host.get_client("ssh")
        conn = client.connect()
        for c in commands:
            conn.run(c)
    else:
        client_configs = [x for x in host.config.client if x['type'] == "ssh"]
        if not client_configs:
            echo_line(env.fail(f"No ssh configurations in host {host.config.host}"))
            return

        cfg = client_configs[0]
        key = env.get_key(cfg["key"])
        with temp_key_file() as key_file:
            key_file.write(key)
            key_file.close()

            os.chmod(key_file.name, 0o600)
            echo_line(env.visible(f"Opening SSH terminal to {host.config.host}"))
            ssh_cmd = f'ssh -i {key_file.name} -o BatchMode=yes -p 22 {cfg["user"]}@{host.config.host} 2> ssh-error.log'
            echo_line(env.visible(f" > {ssh_cmd}"), "\n")
            subprocess.run(ssh_cmd, shell=True)
