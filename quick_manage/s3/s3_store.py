import json

from dacite import from_dict
from minio import Minio, S3Error
from minio.datatypes import Object
from urllib3.response import HTTPResponse
from typing import List, Generator, Dict, Optional, Tuple
from io import BytesIO

from quick_manage.s3 import S3Config
from ..impl_helpers import KeyStoreIndex, sha1_digest
from ..impl_helpers.serialization import as_dict_strip
from ..keys import IKeyStore, Secret


class S3Store(IKeyStore):

    @property
    def type_name(self) -> str:
        return "S3"

    def __init__(self, config: S3Config):
        self.config = config
        self._prefix = self.config.prefix.strip("/") if self.config.prefix is not None else None
        self._index_path = self._name("index.json")

    def put_value(self, secret_name: str, key_name: Optional[str], value: str):
        client = self.config.make_client()
        index = self._read_index(client)
        sha = sha1_digest(value)
        if not key_name:
            key_name = "default"
        target = index.find_or_create(secret_name)

        if target.keys is None:
            target.keys = {}
        target.keys[key_name] = sha

        self._write_index(index, client)

        raw_bytes = value.encode("utf-8")
        buffer = BytesIO(raw_bytes)
        client.put_object(self.config.bucket, self._name(sha), buffer, len(raw_bytes))

    def rm(self, secret_name: str, key_name: Optional[str]):
        client = self.config.make_client()
        index, target, sha = self._find_key(secret_name, key_name, client)

        # If no other secret/key uses this hash, we may delete the file
        used = [h for s in index.secrets for h in s.keys.values() if h == sha]
        if len(used) == 1:
            client.remove_object(self.config.bucket, self._name(sha))

        if len(target.keys) == 1:
            # This is the only key left, we can delete the whole secret
            index.secrets.remove(target)
        else:
            del target.keys[key_name]

        self._write_index(index, client)

    def get_value(self, secret_name: str, key_name: Optional[str]) -> str:
        client = self.config.make_client()
        index, target, sha = self._find_key(secret_name, key_name, client)

        result: HTTPResponse = client.get_object(self.config.bucket, self._name(sha))
        return result.data.decode("utf-8")

    def get_meta(self, secret_name: str) -> Secret:
        client = self.config.make_client()
        index, target = self._find_secret(secret_name, client)
        return target

    def set_meta(self, secret_name: str, value: Dict):
        client = self.config.make_client()
        index, target = self._find_secret(secret_name, client)
        target.meta_data = value
        self._write_index(index, client)

    def all(self) -> Dict[str, Secret]:
        client = self.config.make_client()
        index = self._read_index(client)
        return {x.name: x for x in index.secrets}

    def _find_secret(self, secret_name, client: Minio) -> Tuple[KeyStoreIndex, Secret]:
        index = self._read_index(client)

        target = index.find_secret(secret_name)
        if not target:
            raise KeyError(f"No secret named '{secret_name}' was found")

        return index, target

    def _find_key(self, secret_name, key_name, client: Minio) -> Tuple[KeyStoreIndex, Secret, str]:
        index, target = self._find_secret(secret_name, client)
        if not key_name:
            key_name = "default"

        if key_name not in target.keys:
            raise KeyError(f"No key named '{key_name}' found in secret '{secret_name}'")

        return index, target, target.keys[key_name]

    def _write_index(self, index: KeyStoreIndex, client: Minio):
        raw_bytes = json.dumps(as_dict_strip(index)).encode("utf-8")
        buffer = BytesIO(raw_bytes)
        client.put_object(self.config.bucket, self._index_path, buffer, len(raw_bytes))

    def _read_index(self, client: Minio) -> KeyStoreIndex:
        try:
            result: HTTPResponse = client.get_object(self.config.bucket, self._index_path)
        except S3Error as e:
            if e.code == "NoSuchKey":
                return KeyStoreIndex()
            raise

        text = result.data.decode("utf-8")
        return from_dict(KeyStoreIndex, json.loads(text))

    def _name(self, *args) -> str:
        pieces = [self._prefix] + list(args) if self._prefix else list(args)
        return "/".join(pieces)

