import click
import quick_manage.certificates


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.core.Context):
    pass


main.add_command(quick_manage.certificates.cert)
