from __future__ import annotations
import json
from typing import Optional, Callable, Dict

import click
from .config import QuickConfig
from .context import ContextBuilder
from .context.local_file_context import LocalFileContext

from quick_manage.config import QuickConfig
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


class Environment:
    def __init__(self, config: QuickConfig):
        self.config = config
        self.json = False

        # Shortcuts for styles
        self.fail = config.styles.fail
        self.warning = config.styles.warning
        self.visible = config.styles.visible
        self.success = config.styles.success

        # Default context builder
        self.context_builder = ContextBuilder()
        self.context_builder.register("filesystem", LocalFileContext, LocalFileContext.Config)
    #
    #     # Load the key stores
    #     self.key_stores = {}
    #     self.default_key_store = None
    #     for name, item in config.key_stores.items():
    #         try:
    #             store = create_store(item)
    #             if self.default_key_store is None or item.get("default", False):
    #                 self.default_key_store = name
    #             self.key_stores[name] = store
    #         except Exception as e:
    #             echo_line(config.styles.fail(f"Error loading key store '{name}': {e}"), err=True)
    #
    #     # Load the stored certificate list
    #     self.certs = {}
    #     for item in config.certs:
    #         self.certs[item['name']] = StoredCert(**item)
    #
    #     # Load the stored hosts
    #     self.host_configs = {}
    #     for item in config.hosts:
    #         self.host_configs[item["host"]] = HostConfig(**item)
    #
    # def list_keys(self, store_name: Optional[str] = None):
    #     results = {}
    #     if store_name is not None and store_name not in self.key_stores:
    #         raise KeyError(f"No key store named '{store_name}'")
    #
    #     to_iterate = self.key_stores.items() if store_name is None else [
    #         (store_name, self.key_stores.get(store_name, None))
    #     ]
    #
    #     for name, store in to_iterate:
    #         try:
    #             results[name] = {"keys": store.list(), "error": None, "default": name == self.default_key_store}
    #         except Exception as e:
    #             results[name] = {"keys": [], "error": f"{e}", "default": name == self.default_key_store}
    #     return results
    #
    # def rm_key(self, name: str, store_name):
    #     """ Attempt to remove the key from the specified store. """
    #     store = self._get_store(store_name)
    #     store.rm(name)
    #
    # def get_key(self, name: str, store_name: Optional[str] = None) -> str:
    #     """ Attempt to get the key from the specified store. If no store was specified, the default is attempted,
    #     and then every other store is checked. """
    #     store = self._get_store(store_name)
    #     if name in store.list():
    #         return store.get(name)
    #
    #     if store_name is None:
    #         for _store_name, store in self.key_stores.items():
    #             if _store_name == self.default_key_store:
    #                 continue
    #             if name in store.list():
    #                 return store.get(name)
    #
    #     raise KeyError(f"The key '{name}' was not found")
    #
    # def put_key(self, name: str, value: str, store_name: Optional[str] = None):
    #     store = self._get_store(store_name)
    #     store.put(name, value)
    #
    # def _get_store(self, store_name=None) -> KeyStore:
    #     if store_name is None:
    #         store_name = self.default_key_store
    #
    #     store: KeyStore = self.key_stores.get(store_name, None)
    #     if store is None:
    #         raise KeyError(f"No key store named '{store_name}' was found")
    #     return store
    #
    # def _host_client_factory(self, host: str, client_config: Dict):
    #     client_type = client_config['type']
    #     if client_type == "ssh":
    #         def factory():
    #             key = self.get_key(client_config["key"])
    #             from quick_manage.ssh.client import SSHClient
    #             client = SSHClient(client_config["user"], host, key_data=key)
    #             return client
    #         return factory
    #
    #     else:
    #         raise ValueError(f"No client of type '{client_type}")
    #
    # def get_host(self, host_name: str) -> Host:
    #     cfg = self.host_configs[host_name]
    #     return Host(cfg, self.certs, self._host_client_factory(cfg.host, cfg.client[0]))

    @staticmethod
    def default() -> Environment:
        config = QuickConfig.default()
        return Environment(config)
