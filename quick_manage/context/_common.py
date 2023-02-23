from abc import ABC
from dataclasses import dataclass
from typing import Dict, Type, List
from dacite import from_dict
from dacite.core import T

from .._common import EntityConfig, EntityTypeBuildInfo
from ..keys import IKeyStore
from ..hosts import Host


class IContext(ABC):

    @property
    def key_stores(self) -> Dict[str, IKeyStore]:
        raise NotImplementedError()

    @property
    def host_names(self) -> List[str]:
        raise NotImplementedError()

    @property
    def hosts(self) -> Dict[str, Host]:
        raise NotImplementedError()