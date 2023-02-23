import os.path

import click
import quick_manage.cli.certificates
import quick_manage.cli.hosts
import quick_manage.cli.keys
import quick_manage.cli.ssh
import quick_manage.cli.context

from quick_manage.environment import Environment, echo_line

ENTRY_POINT = "quick"


@click.group()
@click.pass_context
def main(ctx: click.core.Context):
    pass


@main.command()
@click.pass_context
def autocomplete(ctx: click.core.Context):
    env = Environment.default()

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
main.add_command(quick_manage.cli.ssh.main)
main.add_command(quick_manage.cli.context.main)
