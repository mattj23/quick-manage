from dataclasses import dataclass
from io import BytesIO
from typing import Optional, List, Dict, Callable
from quick_manage.certs import StoredCert, get_cert_info_from_server
from quick_manage.ssh.client import SSHClient


@dataclass
class HostCertConfig:
    endpoint: str
    cert: str
    full_chain: str
    key: str
    post_actions: List[Dict]


@dataclass
class HostConfig:
    host: str
    client: List[Dict]
    certs: List[Dict]
    description: Optional[str] = None


class HostCert:
    def __init__(self, config: HostCertConfig, stored: StoredCert, get_client: Callable[[], SSHClient]):
        self.config = config
        self.stored = stored
        self._get_client = get_client

    def should_update(self) -> bool:
        on_host = get_cert_info_from_server(self.config.endpoint)
        in_storage = self.stored.get_info()

        if in_storage.days_remaining() > 0 and in_storage.not_after > on_host.not_after:
            # This certificate is newer than the one on the server
            return True

        return False

    def update(self):
        client = self._get_client()
        connection = client.connect()

        # Copy the files
        # TODO: Make this generic
        for component, access in self.stored.access_components().items():
            if hasattr(self.config, component):
                content = access.get()
                value = getattr(self.config, component)
                if isinstance(value, str):
                    destinations = [value]
                elif isinstance(value, list):
                    destinations = value
                else:
                    raise ValueError(f"Cannot get destinations from: {value}")

                for dest in destinations:
                    payload = BytesIO(content)
                    connection.put(payload, dest)

        for action in self.config.post_actions:
            if action["type"] == "ssh":
                for command in action["commands"]:
                    connection.run(command, pty=True)


class Host:
    def __init__(self, config: HostConfig, stored_certs: Dict[str, StoredCert], get_client):
        self.config = config
        self._certs = None
        self._stored_certs = stored_certs
        self._get_client = get_client

    @property
    def certs(self) -> List[HostCert]:
        if self._certs is None:
            self._certs = []
            for config_dict in self.config.certs:
                config = HostCertConfig(**config_dict)
                stored = self._stored_certs[config.cert]
                self._certs.append(HostCert(config, stored, self._get_client))
        return self._certs

    def get_client(self, type_name: str):
        return self._get_client()
