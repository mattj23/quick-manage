from dataclasses import dataclass

import minio


@dataclass
class S3Config:
    url: str
    bucket: str
    prefix: str
    access_key: str
    secret_key: str
