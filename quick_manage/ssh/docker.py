import json
import re
from typing import Callable, Dict

from quick_manage.ssh.ssh_client import RemoteClient


class Docker:
    def __init__(self, client: RemoteClient, binary: str = "docker", sudo: bool = True):
        self._client = client
        self._binary = binary
        self._sudo = sudo

    def _base_command(self):
        return ("sudo " if self._sudo else "") + self._binary

    def get_containers(self):
        command = self._base_command() + " container ls --all --no-trunc --format='{{json .}}'"
        result = self._client.run_command(command)
        result.raise_if_error()

        entities = [json.loads(x) for x in result.stdout.split("\n") if x.strip()]
        return entities

    def restart_container_by_id(self, container_id):
        print(f"Restarting docker container {container_id}")
        command = self._base_command() + f" restart {container_id}"
        result = self._client.run_command(command)
        result.raise_if_error()

    def restart_containers_by_match(self, match: Callable[[Dict], bool]):
        containers = self.get_containers()
        for item in containers:
            if match(item):
                self.restart_container_by_id(item["ID"])


def name_exact(name: str) -> Callable[[Dict], bool]:
    def predicate(item: Dict) -> bool:
        return item["Names"] == name

    return predicate


def name_regex(pattern: str) -> Callable[[Dict], bool]:
    regex = re.compile(pattern)

    def predicate(item: Dict) -> bool:
        return regex.match(item["Names"]) is not None

    return predicate
