import click
from quick_manage.config import Config
from quick_manage.keys.stores import create_store, KeyStore


def echo_line(*args: str):
    if not args:
        click.echo()
        return

    for chunk in args[:-1]:
        click.echo(chunk, nl=False)
    click.echo(args[-1])


class Environment:
    def __init__(self, config: Config):
        self.config = config
        self.key_store = create_store(config.key_store)
