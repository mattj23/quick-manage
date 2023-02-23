import json
import os.path
from typing import Dict, Optional, List

from dataclasses import dataclass, field

from dacite import from_dict

from .._common import EntityConfig, Builders
from ..file import IFileProvider, FileSystem
from ..hosts import Host, HostConfig
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
        self._hosts_folder = os.path.join(self.config.path, "hosts")
        self._key_stores: Optional[Dict[str, IKeyStore]] = None
        self._builders = builders
        self._files = file_system if file_system else FileSystem()
        self._host_configs: Optional[List[HostConfig]] = None
        self._hosts: Optional[Dict[str, Host]] = None

    @property
    def key_stores(self) -> Dict[str, IKeyStore]:
        if self._key_stores:
            return self._key_stores

        # This local file context should automatically create a local key store if one doesn't exist
        if not self._files.exists(self._path_key_stores):
            self._files.mkdirs(self.config.path)
            key_cfg = LocalFileContext.KeyStoresConfig()
            key_cfg.stores.append(EntityConfig("local", "folder",
                                               {"path": os.path.join(self.config.path, "local-store")}))
            with self._files.write_file(self._path_key_stores) as handle:
                to_yaml(key_cfg, handle)

        with self._files.read_file(self._path_key_stores) as handle:
            stores_config: LocalFileContext.KeyStoresConfig = from_yaml(LocalFileContext.KeyStoresConfig, handle)

        self._key_stores = {c.name: self._builders.key_store.build(c) for c in stores_config.stores}
        return self._key_stores

    @property
    def host_names(self) -> List[str]:
        return [x.host for x in self._get_host_configs()]

    @property
    def hosts(self) -> Dict[str, Host]:
        if self._hosts is None:
            self._hosts = {c.host: Host(c, self._builders.clients, self.key_stores) for c in self._get_host_configs()}
        return self._hosts

    def _get_host_configs(self) -> List[HostConfig]:
        if self._host_configs is None:
            self._host_configs = []
            if not self._files.exists(self._hosts_folder):
                self._files.mkdirs(self._hosts_folder)
            host_config_files = self._files.get_all(self._hosts_folder)
            for f in host_config_files:
                with self._files.read_file(os.path.join(self._hosts_folder, f.file_name)) as handle:
                    self._host_configs.append(from_yaml(HostConfig, handle))

        return self._host_configs
