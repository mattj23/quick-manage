from abc import ABC
from dataclasses import dataclass
from typing import Dict, Type, List, Optional
from dacite import from_dict
from dacite.core import T
from .._common import EntityConfig, EntityTypeBuildInfo

_valid_pattern = None


def _validate_secret_name(name: str) -> bool:
    global _valid_pattern
    if _valid_pattern is None:
        import re
        _valid_pattern = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_\-/.]*[A-Za-z0-9_]$")
    return _valid_pattern.match(name) is not None


@dataclass
class Secret:
    name: str
    meta_data: Optional[Dict] = None
    keys: Optional[Dict[str, Optional[str]]] = None

    def __post_init__(self):
        if not _validate_secret_name(self.name):
            raise ValueError(f"The secret name '{self.name}' is not valid. Alphanumeric, period, forward slash, "
                             f"underscore, and dashes are allowed, with the first and last characters alphanumeric "
                             f"only.")

    @staticmethod
    def name_is_valid(name: str) -> bool:
        return _validate_secret_name(name)


class IKeyStore(ABC):
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
