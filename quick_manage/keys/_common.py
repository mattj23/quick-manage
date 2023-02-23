from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, Type, List, Optional

import click
from dacite import from_dict
from dacite.core import T
from .._common import EntityConfig, EntityTypeBuildInfo

__valid_key_pattern = None
__python_invalid_pattern = None


def python_variable_name(name: str) -> str:
    return _python_invalid_pattern().sub("_", name.lower())


def _python_invalid_pattern():
    global __python_invalid_pattern
    if __python_invalid_pattern is None:
        import re
        __python_invalid_pattern = re.compile(r"[^a-z0-9_]")
    return __python_invalid_pattern


def _valid_key_pattern():
    global __valid_key_pattern
    if __valid_key_pattern is None:
        import re
        __valid_key_pattern = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_\-.]*[A-Za-z0-9_]$")
    return __valid_key_pattern


def _validate_key_name(name: str) -> bool:
    return _valid_key_pattern().match(name) is not None


def _validate_secret_name(name: str) -> bool:
    pattern = _valid_key_pattern()
    parts = name.split("/")
    return all(pattern.match(x) is not None for x in parts)


@dataclass
class Secret:
    name: str
    meta_data: Optional[Dict] = None
    keys: Optional[Dict[str, Optional[str]]] = None

    def __post_init__(self):
        # Validate the name/path
        if not _validate_secret_name(self.name):
            raise ValueError(f"The secret name '{self.name}' is not valid. Alphanumeric, period, forward slash, "
                             f"underscore, and dashes are allowed, with the first and last characters alphanumeric "
                             f"only.")

        # Validate all keys
        if self.keys:
            for k in self.keys.keys():
                if not _validate_key_name(k):
                    raise ValueError(
                        f"The key name '{k}' is not valid. Alphanumeric, period, underscore, and dashes are allowed, "
                        f"with the first and last characters alphanumeric only.")

    def get_keys(self) -> Dict[str, Optional[str]]:
        return self.keys if self.keys else {}

    def get_type_name(self) -> Optional[str]:
        if self.meta_data:
            return self.meta_data.get("type", None)
        return None

    @staticmethod
    def key_is_valid(key_name: str) -> bool:
        return _validate_key_name(key_name)

    @staticmethod
    def name_is_valid(name: str) -> bool:
        return _validate_secret_name(name)


@dataclass
class SecretPath:
    original: str
    store: str
    secret: Optional[str] = None
    key: Optional[str] = None

    @staticmethod
    def from_text(text: str) -> SecretPath:
        store, *secret_leftover = text.split("/", 1)
        if secret_leftover:
            secret, *key = secret_leftover[0].split("@")
            if key:
                return SecretPath(text, store, secret, key[0])
            return SecretPath(text, store, secret)
        return SecretPath(text, store)


@dataclass
class SecretType:
    name: str
    keys: List[str] = field(default_factory=list)


class KeyGetter:
    """ A read-only object which can retrieve key values by their path. """
    def __init__(self, stores: Dict[str, IKeyStore]):
        self._stores = stores

    def get(self, key_path: str) -> str:
        path = SecretPath.from_text(key_path)
        key_store = self._stores.get(path.store, None)
        if key_store is None:
            raise KeyError(f"No key store named '{path.store}' in this context")
        return key_store.get_value(path.secret, path.key)


class IKeyStore(ABC):
    @property
    def type_name(self) -> str:
        raise NotImplementedError()

    def put_value(self, secret_name: str, key_name: Optional[str], value: str):
        raise NotImplementedError()

    def rm(self, secret_name: str, key_name: Optional[str]):
        raise NotImplementedError()

    def get_value(self, secret_name: str, key_name: Optional[str]) -> str:
        raise NotImplementedError()

    def get_meta(self, secret_name: str) -> Secret:
        raise NotImplementedError()

    def set_meta(self, secret_name: str, value: Dict):
        raise NotImplementedError()

    def all(self) -> Dict[str, Secret]:
        raise NotImplementedError()

    def has_secret(self, secret_name: str) -> bool:
        return secret_name in self.all()


class IKeyCreateCommand(ABC):
    @property
    def name(self) -> str:
        raise NotImplementedError()

    @property
    def secret_type_name(self) -> str:
        raise NotImplementedError()

    def configure_command(self, command: click.Command):
        raise NotImplementedError()

    def on_create(self, **kwargs) -> Dict[str, str]:
        raise NotImplementedError()

    @property
    def help(self) -> str:
        raise NotImplementedError()
