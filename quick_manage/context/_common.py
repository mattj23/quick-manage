from dataclasses import dataclass
from typing import Dict


@dataclass
class ContextConfig:
    name: str
    type: str
    config: Dict


class Context:
    def __init__(self):
        self.key_stores = {}
        self.hosts = {}
        self.certs = {}

