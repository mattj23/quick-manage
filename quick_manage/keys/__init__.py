import abc
from typing import List, Dict, Tuple


class KeyStore(abc.ABC):
    def put(self, key_name: str, value: str):
        raise NotImplementedError()

    def get(self, key_name: str) -> str:
        raise NotImplementedError()

    def list(self) -> List[str]:
        raise NotImplementedError()


def create_store(store_info: Dict) -> KeyStore:
    if store_info["type"] == "config-folder":
        from quick_manage.keys.file_store import FileStore
        return FileStore()

    elif store_info["type"] == "s3":
        from quick_manage.keys.s3_store import S3Store, S3Config
        config_kwargs = dict(store_info["config"])
        config = S3Config(**config_kwargs)
        return S3Store(config)

    else:
        raise ValueError("No key store for configuration info of type {type}".format(**store_info))
