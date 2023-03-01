from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from typing import Optional, List, Dict, Callable

from quick_manage._common import IBuilder, EntityConfig, HostClient, ClientAction
from quick_manage.keys import IKeyStore, KeyGetter


@dataclass
class DeployConfig:
    client: str
    fullchain: Optional[str] = None
    private: Optional[str] = None
    cert: Optional[str] = None
    chain: Optional[str] = None
    post: Optional[List[ClientAction]] = None


@dataclass
class HostCertConfig:
    name: str
    secret: str
    deploy: DeployConfig


@dataclass
class HostConfig:
    host: str
    network: Dict
    clients: List[EntityConfig]
    certs: List[HostCertConfig]
    description: Optional[str] = None


class Host:
    def __init__(self, config: HostConfig, client_builder: IBuilder, key_stores: Dict[str, IKeyStore]):
        self.config = config
        self._certs = None
        self._client_builder = client_builder
        self._key_getter = KeyGetter(key_stores)

    def get_client_by_type(self, type_name) -> Optional[HostClient]:
        for item in self.config.clients:
            if item.type == type_name:
                return self._client_builder.build(item, key_getter=self._key_getter, nets=self.config.network)
        return None

    def get_client_by_name(self, name) -> Optional[HostClient]:
        for item in self.config.clients:
            if item.name == name:
                return self._client_builder.build(item, key_getter=self._key_getter, nets=self.config.network)
        return None

    def deploy_cert(self, config: HostCertConfig, message: Optional[Callable[[str], None]] = None):
        # Get the push client
        push_client = self.get_client_by_name(config.deploy.client)
        if push_client is None:
            raise KeyError(f"No client named {config.deploy.client} for certificate deployment")

        for sub_key in ["fullchain", "private", "chain", "cert"]:
            deploy_value = getattr(config.deploy, sub_key)

            if deploy_value:
                if message:
                    message(f"Putting {sub_key} at {deploy_value}")
                data = self._key_getter.get(f"{config.secret}@{sub_key}")
                push_client.put_data(deploy_value, data)

        if config.deploy.post:
            if message:
                message("Running post-deployment commands")

            for post_action in config.deploy.post:
                post_client = self.get_client_by_name(post_action.client)
                if post_client is None:
                    raise KeyError(f"No client named {post_action.client} for post-certificate deployment actions")

                for command in post_action.actions:
                    if message:
                        message(f" * {command}")

                    post_client.action(command)
