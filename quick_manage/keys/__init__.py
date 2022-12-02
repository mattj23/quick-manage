import abc
from typing import List


class KeyStore(abc.ABC):
    def put(self, key_name: str, value: str):
        raise NotImplementedError()

    def get(self, key_name: str) -> str:
        raise NotImplementedError()

    def list(self) -> List[str]:
        raise NotImplementedError()
