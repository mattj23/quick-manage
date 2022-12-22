from abc import ABC
from dataclasses import dataclass
from typing import Dict, Type
from dacite import from_dict
from dacite.core import T

from quick_manage._common import EntityConfig, EntityTypeBuildInfo
from quick_manage.keys import IKeyStore


class IContext(ABC):

    @property
    def key_stores(self) -> Dict[str, IKeyStore]:
        raise NotImplementedError()

