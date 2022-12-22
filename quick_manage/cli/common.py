from __future__ import annotations
from dataclasses import dataclass
from typing import List

import click
from click import Context, Parameter, ParamType, echo
from click.shell_completion import CompletionItem

from quick_manage.environment import Environment


class HostNameType(ParamType):
    name = "host-name"

    def shell_complete(self, ctx: Context, param: Parameter, incomplete: str) -> List[CompletionItem]:
        env = Environment.default()
        return [CompletionItem(x) for x in env.host_configs.keys() if x.startswith(incomplete)]


class StoreVarType(ParamType):
    name = "key-store"

    def shell_complete(self, ctx: Context, param: Parameter, incomplete: str) -> List[CompletionItem]:
        env = Environment.default()
        return [CompletionItem(x) for x in env.key_stores.keys() if x.startswith(incomplete)]


@dataclass
class SecretPath:
    original: str
    store: str
    secret: str = ""

    @staticmethod
    def from_text(text: str) -> SecretPath:
        return SecretPath(text, *text.split("/", 1))


class SecretPathType(ParamType):
    name = "secret-path"

    def shell_complete(self, ctx: Context, param: Parameter, incomplete: str) -> List[CompletionItem]:
        env = Environment.default()
        qc = env.active_context

        # Do we have a store name specified in the path yet
        path = SecretPath.from_text(incomplete)
        if path.secret:
            key_store = qc.key_stores.get(path.store, None)
            if key_store is None:
                return []

            full_paths = [f"{path.store}/{x}" for x in key_store.all().keys()]
            return [CompletionItem(x) for x in full_paths if x.startswith(incomplete)]

        else:
            candidate_stores = [(k, v) for k, v in qc.key_stores.items() if k.startswith(incomplete)]
            options = []
            for store_name, key_store in candidate_stores:
                full_paths = [f"{store_name}/{x}" for x in key_store.all().keys()]
                options += [CompletionItem(x) for x in full_paths if x.startswith(incomplete)]
            return options


class KeyNameType(ParamType):
    name = "key-name"

    def shell_complete(self, ctx: Context, param: Parameter, incomplete: str) -> List[CompletionItem]:
        return []

        # TODO: this won't work unless the order can be controlled
        qc = Environment.default().active_context
        secret_path = ctx.params.get("secret", None)
        click.echo(ctx.params, err=True)
        if not secret_path:
            return []
        path = SecretPath.from_text(secret_path)

        if not path.secret:
            return []

        key_store = qc.key_stores.get(path.store, None)
        if key_store is None:
            return []

        try:
            secret = key_store.get_meta(path.secret)
            if not secret.keys:
                return []
            return [CompletionItem(x) for x in secret.keys.keys() if x.startswith(incomplete)]
        except KeyError:
            return []
