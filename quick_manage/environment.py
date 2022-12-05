from __future__ import annotations
import json
from typing import Optional

import click
from quick_manage.config import Config, load_config
from quick_manage.keys import create_store, KeyStore
from quick_manage.certs import StoredCert


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
    def __init__(self, config: Config):
        self.config = config
        self.json = False

        # Shortcuts for styles
        self.fail = config.styles.fail
        self.warning = config.styles.warning
        self.visible = config.styles.visible
        self.success = config.styles.success

        # Load the key stores
        self.key_stores = {}
        self.default_key_store = None
        for name, item in config.key_stores.items():
            try:
                store = create_store(item)
                if self.default_key_store is None or item.get("default", False):
                    self.default_key_store = name
                self.key_stores[name] = store
            except Exception as e:
                echo_line(config.styles.fail(f"Error loading key store '{name}': {e}"), err=True)

        # Load the stored certificate list
        self.certs = {}
        for item in config.certs:
            self.certs[item['name']] = StoredCert(**item)

    def list_keys(self, store_name: Optional[str] = None):
        results = {}
        if store_name is not None and store_name not in self.key_stores:
            raise KeyError(f"No key store named '{store_name}'")

        to_iterate = self.key_stores.items() if store_name is None else [
            (store_name, self.key_stores.get(store_name, None))
        ]

        for name, store in to_iterate:
            try:
                results[name] = {"keys": store.list(), "error": None, "default": name == self.default_key_store}
            except Exception as e:
                results[name] = {"keys": [], "error": f"{e}", "default": name == self.default_key_store}
        return results

    def get_key(self, name: str, store_name: Optional[str] = None) -> str:
        """ Attempt to get the key from the specified store. If no store was specified, the default is attempted,
        and then every other store is checked. """
        store = self._get_store(store_name)
        if name in store.list():
            return store.get(name)

        if store_name is None:
            for _store_name, store in self.key_stores.items():
                if _store_name == self.default_key_store:
                    continue
                if name in store.list():
                    return store.get(name)

        raise KeyError(f"The key '{name}' was not found")

    def put_key(self, name: str, value: str, store_name: Optional[str] = None):
        store = self._get_store(store_name)
        store.put(name, value)

    def _get_store(self, store_name=None) -> KeyStore:
        if store_name is None:
            store_name = self.default_key_store

        store: KeyStore = self.key_stores.get(store_name, None)
        if store is None:
            raise KeyError(f"No key store named '{store_name}' was found")
        return store

    @staticmethod
    def default() -> Environment:
        config = load_config()
        return Environment(config)
