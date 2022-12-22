from abc import ABC
from dataclasses import dataclass
from typing import Dict, Type, List
from dacite import from_dict
from dacite.core import T
from .._common import EntityConfig, EntityTypeBuildInfo


class IKeyStore(ABC):
    def put(self, key_name: str, value: str):
        raise NotImplementedError()

    def rm(self, key_name: str):
        raise NotImplementedError()

    def get(self, key_name: str) -> str:
        raise NotImplementedError()

    def list(self) -> List[str]:
        raise NotImplementedError()

