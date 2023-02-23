from __future__ import annotations
from dataclasses import dataclass
from typing import List

import click
from click import Context, Parameter, ParamType, echo
from click.shell_completion import CompletionItem

from quick_manage.environment import Environment
from quick_manage.keys import SecretPath


class HostNameType(ParamType):
    name = "host-name"

    def shell_complete(self, ctx: Context, param: Parameter, incomplete: str) -> List[CompletionItem]:
        env = Environment.default()
        return [CompletionItem(x) for x in env.active_context.host_names if x.startswith(incomplete)]


class StoreVarType(ParamType):
    name = "key-store"

    def shell_complete(self, ctx: Context, param: Parameter, incomplete: str) -> List[CompletionItem]:
        env = Environment.default()
        return [CompletionItem(x) for x in env.active_context.key_stores.keys() if x.startswith(incomplete)]


class KeyPathType(ParamType):
    name = "key-path"

    def shell_complete(self, ctx: Context, param: Parameter, incomplete: str) -> List[CompletionItem]:
        env = Environment.default()
        qc = env.active_context

        path = SecretPath.from_text(incomplete)

        if path.secret:
            # We already have the completed store name and some/part of the path
            key_store = qc.key_stores.get(path.store, None)
            if key_store is None:
                return []

            if path.key:
                # We also have part of the key, so the secret name must be completed
                try:
                    secret_info = key_store.get_meta(path.secret)
                    secret_keys = secret_info.keys if secret_info.keys else {}
                    full_paths = [f"{path.store}/{path.secret}@{k}" for k in secret_keys.keys()]
                    return [CompletionItem(x) for x in full_paths if x.startswith(incomplete)]
                except KeyError:
                    return []

            # We do not have any of the key, so we should find all possible secrets and keys which might match
            options = []
            for s in key_store.all().values():
                if s.name.startswith(path.secret):
                    for k in (s.keys.keys() if s.keys else {}):
                        options.append(CompletionItem(f"{path.store}/{s.name}@{k}"))
            return options

        else:
            # At this point we only have part of the store name, so we must retrieve all secrets and their keys
            candidate_stores = [(k, v) for k, v in qc.key_stores.items() if k.startswith(incomplete)]
            options = []
            for store_name, key_store in candidate_stores:
                for s in key_store.all().values():
                    for k in (s.keys.keys() if s.keys else {}):
                        options.append(CompletionItem(f"{store_name}/{s.name}@{k}"))
            return options


class SecretPathType(ParamType):
    name = "secret-path"

    def shell_complete(self, ctx: Context, param: Parameter, incomplete: str) -> List[CompletionItem]:
        env = Environment.default()
        qc = env.active_context

        path = SecretPath.from_text(incomplete)

        if path.secret:
            # We already have the completed store name and some/part of the path
            key_store = qc.key_stores.get(path.store, None)
            if key_store is None:
                return []

            # We do not have any of the key, so we should find all possible secrets and keys which might match
            options = []
            for s in key_store.all().values():
                if s.name.startswith(path.secret):
                    options.append(CompletionItem(f"{path.store}/{s.name}"))
            return options

        else:
            # At this point we only have part of the store name, so we must retrieve all secrets and their keys
            candidate_stores = [(k, v) for k, v in qc.key_stores.items() if k.startswith(incomplete)]
            options = []
            for store_name, key_store in candidate_stores:
                for s in key_store.all().values():
                    options.append(CompletionItem(f"{store_name}/{s.name}"))
            return options
