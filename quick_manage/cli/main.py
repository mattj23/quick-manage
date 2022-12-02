import click
import quick_manage.cli.certificates
import quick_manage.cli.hosts
import quick_manage.cli.keys

from quick_manage.config import load_config
from quick_manage.environment import Environment


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.core.Context):
    config = load_config()
    environment = Environment(config)
    ctx.obj = environment


main.add_command(quick_manage.cli.certificates.cert)
main.add_command(quick_manage.cli.hosts.host_command)
main.add_command(quick_manage.cli.keys.main)
