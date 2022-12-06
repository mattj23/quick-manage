import os
from typing import Dict, List

from ..config import CONFIG_FOLDER


class FileStore(KeyStore):
    def __init__(self):
        self.folder = os.path.join(CONFIG_FOLDER, "keys")
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
            os.chmod(self.folder, 0o700)

    def _path(self, key: str) -> str:
        path_base = os.path.abspath(self.folder)
        dest_path = os.path.abspath(os.path.join(path_base, key))
        if not dest_path.startswith(path_base):
            raise ValueError(f"Path '{dest_path}' escapes '{path_base}'")
        return dest_path

    def rm(self, key_name: str):
        os.remove(self._path(key_name))

    def get(self, key_name: str) -> str:
        if not os.path.exists(self._path(key_name)):
            raise KeyError(f"Key {key_name} not found")

        with open(self._path(key_name), "r") as handle:
            return handle.read()

    def put(self, key_name: str, value: str):
        with open(self._path(key_name), "w") as handle:
            handle.write(value)

        os.chmod(self._path(key_name), 0o700)

    def list(self) -> List[str]:
        return os.listdir(self.folder)

