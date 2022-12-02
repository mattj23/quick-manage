import os
from typing import Dict, List

from ..keys import KeyStore
from ..config import CONFIG_FOLDER


class FileStore(KeyStore):
    def __init__(self):
        self.folder = os.path.join(CONFIG_FOLDER, "keys")
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
            os.chmod(self.folder, 0o700)

    def _path(self, key: str) -> str:
        return os.path.join(self.folder, key)

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

