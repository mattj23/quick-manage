from typing import Dict, Optional, List
from dataclasses import dataclass, field

from ..keys import Secret, IKeyStore


@dataclass
class KeyStoreIndex:
    secrets: List[Secret] = field(default_factory=list)

    def find_secret(self, secret_name: str) -> Optional[Secret]:
        matches = [x for x in self.secrets if x.name == secret_name]
        return matches[0] if matches else None

    def create_secret(self, secret_name: str) -> Secret:
        if any(x for x in self.secrets if x.name == secret_name):
            raise KeyError(f"The key store already has a secret named '{secret_name}'")

        secret = Secret(secret_name)
        self.secrets.append(secret)
        return secret

    def find_or_create(self, secret_name: str) -> Secret:
        found = self.find_secret(secret_name)
        return found if found else self.create_secret(secret_name)


def sha1_digest(text: str) -> str:
    import hashlib
    return hashlib.sha1(text.encode("utf-8")).hexdigest()
