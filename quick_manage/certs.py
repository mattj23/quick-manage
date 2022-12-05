from __future__ import annotations

import base64
import re
import ssl
import socket

from dataclasses import dataclass, asdict
from datetime import datetime as DateTime
from typing import Dict, Any

from cryptography import x509
from cryptography.hazmat.primitives.hashes import SHA1

from quick_manage.files import FileAccess, create_access

_server_pattern = re.compile(r"^([\da-zA-Z.\-]+)(:\d+)?$")


@dataclass
class CertInfo:
    not_before: DateTime
    not_after: DateTime
    issuer: str
    serial: int
    fingerprint: str
    signature: str

    def days_remaining(self) -> float:
        return (self.not_after - DateTime.now()).days

    def serializable(self) -> Dict:
        result = asdict(self)
        result["not_before"] = self.not_before.isoformat()
        result["not_after"] = self.not_after.isoformat()
        return result

    @staticmethod
    def from_x509(certificate) -> CertInfo:
        return CertInfo(not_before=certificate.not_valid_before,
                        not_after=certificate.not_valid_after,
                        issuer=certificate.issuer.rfc4514_string(),
                        serial=certificate.serial_number,
                        fingerprint=certificate.fingerprint(SHA1()).hex(),
                        signature=base64.b64encode(certificate.signature).decode())


@dataclass
class StoredCert:
    name: str
    storage: str
    config: Dict
    full_chain: str
    key: str
    chain: str
    cert: str

    def access_components(self) -> Dict[str, FileAccess]:
        return {k: create_access(self.storage, self.config, getattr(self, k))
                for k in ("full_chain", "key", "chain", "cert")}

    def access_full(self) -> FileAccess:
        return create_access(self.storage, self.config, self.full_chain)

    def access_key(self) -> FileAccess:
        return create_access(self.storage, self.config, self.key)

    def access_chain(self) -> FileAccess:
        return create_access(self.storage, self.config, self.chain)

    def access_cert(self) -> FileAccess:
        return create_access(self.storage, self.config, self.cert)

    def get_info(self) -> CertInfo:
        access = self.access_cert()
        raw_data = access.get()
        certificate = x509.load_pem_x509_certificate(raw_data)
        return CertInfo.from_x509(certificate)


def get_cert_from_server(target: str):
    matches = _server_pattern.findall(target)
    if not matches:
        raise ValueError(f"Could not parse '{target}' as a hostname/port")

    host_name, port_text = matches[0]
    port = int(port_text.strip(":")) if port_text else 443

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.VerifyMode.CERT_NONE
    connection = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host_name)
    connection.settimeout(3)

    connection.connect((host_name, port))
    info = connection.getpeercert(True)
    return x509.load_der_x509_certificate(info)


def get_cert_info_from_server(target: str):
    cert = get_cert_from_server(target)
    return CertInfo.from_x509(cert)


if __name__ == '__main__':
    pass
