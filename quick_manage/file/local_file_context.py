import os.path
from typing import Dict, Optional, List

from dataclasses import dataclass, field

from .._common import EntityConfig, Builders
from ..file import IFileProvider, FileSystem
from ..impl_helpers import to_yaml, from_yaml
from ..context import IContext
from ..keys import IKeyStore


class LocalFileContext(IContext):
    @dataclass
    class Config:
        path: str

    @dataclass
    class KeyStoresConfig:
        stores: List[EntityConfig] = field(default_factory=list)
        default_store: Optional[str] = None

    def __init__(self, config: Config, builders: Builders, file_system: IFileProvider = None):
        self.config = config
        self._path_key_stores = os.path.join(self.config.path, "key-stores.yaml")
        self._key_stores: Optional[Dict[str, IKeyStore]] = None
        self._builders = builders
        self._files = file_system if file_system else FileSystem()

    @property
    def key_stores(self) -> Dict[str, IKeyStore]:
        if self._key_stores:
            return self._key_stores

        if not self._files.exists(self._path_key_stores):
            return {}

        with self._files.read_file(self._path_key_stores) as handle:
            stores_config: LocalFileContext.KeyStoresConfig = from_yaml(LocalFileContext.KeyStoresConfig, handle)

        self._key_stores = {c.name: self._builders.key_store.build(c) for c in stores_config.stores}
        return self._key_stores


