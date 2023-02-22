import os.path
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field

from ..impl_helpers import to_yaml, from_yaml, KeyStoreIndex, sha1_digest
from ..keys import Secret, IKeyStore
from ._common import IFileProvider
from .file_system import FileSystem


class FolderKeyStore(IKeyStore):
    @property
    def type_name(self) -> str:
        return "Local Folder"

    @dataclass
    class Config:
        path: str

    def __init__(self, config: Config, file_system: Optional[IFileProvider] = None):
        self._file = file_system if file_system else FileSystem()
        self._path = config.path
        self.__index_path: Optional[str] = None

    def put_value(self, secret_name: str, key_name: Optional[str], value: str):
        index = self._read_index()
        sha = sha1_digest(value)
        if not key_name:
            key_name = "default"
        target = index.find_or_create(secret_name)

        if target.keys is None:
            target.keys = {}
        target.keys[key_name] = sha

        self._write_index(index)

        # Save the hash file
        with self._file.write_file(self._key_path(sha)) as handle:
            handle.write(value)

    def rm(self, secret_name: str, key_name: Optional[str]):
        index, target, sha = self._find_key(secret_name, key_name)

        # If no other secret/key uses this hash, we may delete the file
        used = [h for s in index.secrets for h in s.keys.values() if h == sha]
        if len(used) == 1:
            self._file.remove(self._key_path(sha))
        # used =[[h for h in s.keys.values()] for s in index.secrets]

        if len(target.keys) == 1:
            # This is the only key left, we can delete the whole secret
            index.secrets.remove(target)
        else:
            del target.keys[key_name]

        self._write_index(index)

    def get_value(self, secret_name: str, key_name: Optional[str]) -> str:
        index, target, sha = self._find_key(secret_name, key_name)
        with self._file.read_file(self._key_path(sha)) as handle:
            return handle.read()

    def get_meta(self, secret_name: str) -> Secret:
        index, target = self._find_secret(secret_name)
        return target

    def set_meta(self, secret_name: str, value: Dict):
        index, target = self._find_secret(secret_name)
        target.meta_data = value
        self._write_index(index)

    def all(self) -> Dict[str, Secret]:
        index = self._read_index()
        return {x.name: x for x in index.secrets}

    def _find_secret(self, secret_name) -> Tuple[KeyStoreIndex, Secret]:
        index = self._read_index()

        target = index.find_secret(secret_name)
        if not target:
            raise KeyError(f"No secret named '{secret_name}' was found")

        return index, target

    def _find_key(self, secret_name, key_name) -> Tuple[KeyStoreIndex, Secret, str]:
        index, target = self._find_secret(secret_name)
        if not key_name:
            key_name = "default"

        if key_name not in target.keys:
            raise KeyError(f"No key named '{key_name}' found in secret '{secret_name}'")

        return index, target, target.keys[key_name]

    def _key_path(self, sha: str) -> str:
        return os.path.join(self._path, sha)

    @property
    def _index_path(self):
        if self.__index_path is None:
            self.__index_path = os.path.join(self._path, "index.yaml")
        return self.__index_path

    def _write_index(self, index: KeyStoreIndex):
        if not self._file.exists(self._path):
            self._file.mkdirs(self._path)
        with self._file.write_file(self._index_path) as handle:
            to_yaml(index, handle)

    def _read_index(self) -> KeyStoreIndex:
        if not self._file.exists(self._index_path):
            return KeyStoreIndex()
        with self._file.read_file(self._index_path) as handle:
            return from_yaml(KeyStoreIndex, handle)
