from abc import ABC
from typing import Optional, Tuple, List, Dict


class ClientException(Exception):
    def __init__(self, message):
        super(ClientException, self).__init__(message)


class IKeyStore(ABC):
    def put(self, key_name: str, value: str):
        raise NotImplementedError()

    def rm(self, key_name: str):
        raise NotImplementedError()

    def get(self, key_name: str) -> str:
        raise NotImplementedError()

    def list(self) -> List[str]:
        raise NotImplementedError()

    @classmethod
    def type_name(cls) -> str:
        raise NotImplementedError()


class IFileAccess(ABC):
    def get(self) -> bytes:
        pass

    def put(self, value: bytes):
        pass
