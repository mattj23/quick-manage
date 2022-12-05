from abc import ABC
from typing import Dict

from quick_manage.s3 import S3Config


class FileAccess(ABC):
    def get(self) -> bytes:
        pass

    def put(self, value: bytes):
        pass


class S3FileAccess(FileAccess):
    def __init__(self, path: str, config: S3Config):
        self.config = config
        self.path = path
        super(S3FileAccess, self).__init__()

    def get(self) -> bytes:
        client = self.config.make_client()
        path_elements = ([self.config.prefix] if self.config.prefix else []) + [self.path]
        path = "/".join(x.strip("/") for x in path_elements)

        response = client.get_object(self.config.bucket, path)
        return response.data

    def put(self, value: bytes):
        raise NotImplementedError()


def create_access(access_type: str, access_config: Dict, path: str) -> FileAccess:
    if access_type == "s3":
        config = S3Config(**access_config)
        return S3FileAccess(path, config)

    else:
        raise ValueError(f"No file access type for '{access_type}'")
