import os.path

import click
import quick_manage.cli.certificates
import quick_manage.cli.hosts
import quick_manage.cli.keys

from quick_manage.config import load_config
from quick_manage.environment import Environment, echo_line

ENTRY_POINT = "quick"


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.core.Context):
    config = load_config()
    environment = Environment(config)
    ctx.obj = environment


@main.command()
@click.pass_context
def autocomplete(ctx: click.core.Context):
    env: Environment = ctx.obj

    ac_name = f"_{ENTRY_POINT}_COMPLETE".upper().replace("-", "_")
    line = f'eval "$({ac_name}=bash_source {ENTRY_POINT})"'
    home_dir = os.path.expanduser("~")
    bash_rc = os.path.join(home_dir, ".bashrc")

    if not os.path.exists(bash_rc):
        echo_line(env.fail(f"No {bash_rc} file!"), err=True)
        return

    with open(bash_rc, "r") as handle:
        lines = handle.readlines()

    if line in [x.strip() for x in lines]:
        echo_line(env.warning(f"{bash_rc} already contains autocomplete line"))
        return

    with open(bash_rc, "a") as handle:
        handle.write(f"\n{line}\n")

    echo_line(env.visible(f"Autocomplete installed in {bash_rc}"))


main.add_command(quick_manage.cli.certificates.cert)
main.add_command(quick_manage.cli.hosts.host_command)
main.add_command(quick_manage.cli.keys.main)
