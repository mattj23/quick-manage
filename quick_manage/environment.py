from __future__ import annotations
import json
from typing import Optional, Callable, Dict, List

import click

from ._common import Builders
from .config import QuickConfig, Style
from .context import IContext
from .file import FolderKeyStore, LocalFileContext

from .config import QuickConfig
from .keys import SecretType, IKeyCreateCommand, LetsEncryptCertificate
from .s3 import S3Config, S3Store
from .ssh.client import SSHClient


# from quick_manage.keys import create_store, IKeyStore
# from quick_manage.certs import StoredCert
# from quick_manage.hosts import HostConfig, Host


def echo_line(*args: str, err=False):
    if not args:
        click.echo(err=err)
        return

    for chunk in args[:-1]:
        click.echo(chunk, nl=False, err=err)
    click.echo(args[-1], err=err)


def echo_json(item, err=False):
    click.echo(json.dumps(item), err=err)


def echo_table(list_of_rows, spacing=2, header: Optional[Style] = None):
    if len(set(len(r) for r in list_of_rows)) != 1:
        raise Exception("Table must have equal length rows")

    as_columns = list(zip(*list_of_rows))
    widths = [max(len(cell) for cell in col) for col in as_columns]
    all_lines = []
    for row in list_of_rows:
        all_lines.append("".join(f"{cell: <{widths[i] + spacing}}" for i, cell in enumerate(row)))
    if header:
        all_lines[0] = header(all_lines[0])
        # width = max(len(line) for line in all_lines)
        # all_lines = [all_lines[0], "=" * width] + all_lines[1:]
    for line in all_lines:
        echo_line(line)


class Environment:
    _default: Optional[Environment] = None

    def __init__(self, config: QuickConfig):
        self.config = config
        self.json = False

        # Shortcuts for styles
        self.fail = config.styles.fail
        self.warning = config.styles.warning
        self.visible = config.styles.visible
        self.success = config.styles.success
        self.head = config.styles.head

        # Default object builders
        self.builders = Builders()
        self.builders.context.register("filesystem", LocalFileContext, LocalFileContext.Config)

        self.builders.key_store.register("folder", FolderKeyStore, FolderKeyStore.Config)
        self.builders.key_store.register("s3", S3Store, S3Config)

        self.builders.clients.register("ssh", SSHClient, SSHClient.Config)

        # Secret types
        # TODO: these can probably be unified
        self.secret_types: List[SecretType] = [SecretType("ssh-key", ["public", "private"]),
                                               SecretType("certificate", ["fullchain", "chain", "private", "cert"])]
        self.key_creators: List[IKeyCreateCommand] = [LetsEncryptCertificate()]

        self._contexts: Optional[Dict[str, IContext]] = None

    @property
    def contexts(self) -> Dict[str, IContext]:
        build_kwargs = {"builders": self.builders}
        if self._contexts is None:
            # Load contexts
            self._contexts = {c.name: self.builders.context.build(c, **build_kwargs) for c in self.config.contexts}
        return self._contexts

    @property
    def active_context(self) -> IContext:
        return self.contexts[self.config.active_context]

    @staticmethod
    def default() -> Environment:
        if Environment._default is None:
            config = QuickConfig.default()
            Environment._default = Environment(config)
        return Environment._default
