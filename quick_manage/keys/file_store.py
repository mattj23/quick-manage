import os
from typing import Dict, List, Optional
from ._common import IKeyStore
from dataclasses import dataclass, field
from quick_manage.file import IFileProvider, FileSystem


class FileStore(IKeyStore):
    @dataclass
    class Config:
        path: str

    def __init__(self, config: Config, *args, file_system: Optional[IFileProvider] = None, **kwargs):
        self._file = file_system if file_system else FileSystem()
        self.config = config
        if not self._file.exists(self.config.path):
            self._file.mkdirs(self.config.path)
            self._file.chmod(self.config.path, 0o700)

    def _path(self, key: str) -> str:
        # path_base = os.path.abspath(self.config.path)
        # dest_path = os.path.abspath(os.path.join(path_base, key))
        # if not dest_path.startswith(path_base):
        #     raise ValueError(f"Path '{dest_path}' escapes '{path_base}'")
        return os.path.join(self.config.path, key)

    def rm(self, key_name: str):
        self._file.remove(self._path(key_name))

    def get(self, key_name: str) -> str:
        if not self._file.exists(self._path(key_name)):
            raise KeyError(f"Key {key_name} not found")

        with self._file.read_file(self._path(key_name)) as handle:
            return handle.read()

    def put(self, key_name: str, value: str):
        with self._file.write_file(self._path(key_name)) as handle:
            handle.write(value)

        self._file.chmod(self._path(key_name), 0o700)

    def list(self) -> List[str]:
        return [x.file_name for x in self._file.get_all(self.config.path)]
