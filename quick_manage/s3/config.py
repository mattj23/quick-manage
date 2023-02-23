from dataclasses import dataclass
from typing import Optional

from minio import Minio
from urllib3 import Retry, PoolManager


@dataclass
class S3Config:
    endpoint: str
    bucket: str
    access_key: str
    secret_key: str
    prefix: Optional[str] = None
    secure: bool = True
    timeout: float = 1
    retries: int = 1

    def make_client(self) -> Minio:
        http_client = PoolManager(timeout=self.timeout,
                                  retries=Retry(total=self.retries))
        return Minio(self.endpoint,
                     access_key=self.access_key,
                     secret_key=self.secret_key,
                     secure=self.secure,
                     http_client=http_client)
