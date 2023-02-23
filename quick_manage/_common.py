from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, Type, List, Callable, Optional
from dacite import from_dict
from dacite.core import T


@dataclass
class EntityConfig:
    name: str
    type: str
    config: Dict


@dataclass
class EntityTypeBuildInfo:
    type_name: str
    type_class: Type[T]
    config_class: Type[T]
    extra_kwargs: Dict = field(default_factory=dict)


class IBuilder(ABC):
    def register(self, type_name: str, type_class: Type[T], config_class: Type[T], extra_kwargs: Optional[Dict] = None):
        raise NotImplementedError()

    def build(self, config: EntityConfig, **kwargs):
        raise NotImplementedError()


class GenericBuilder(IBuilder):
    def __init__(self, name: str):
        self.name = name
        self._registry: Dict[str, EntityTypeBuildInfo] = {}

    def register(self, type_name: str, type_class: Type[T], config_class: Type[T], extra_kwargs: Optional[Dict] = None):
        self._registry[type_name] = EntityTypeBuildInfo(type_name,
                                                        type_class,
                                                        config_class,
                                                        extra_kwargs if extra_kwargs else {})

    def build(self, config: EntityConfig, **kwargs):
        info = self._registry.get(config.type, None)
        if not info:
            raise KeyError(f"The {self.name} builder has nothing registered for the type '{config.type}'")

        internal_config = from_dict(info.config_class, config.config)
        context = info.type_class(internal_config, **kwargs, **info.extra_kwargs)
        return context

    @staticmethod
    def factory(name: str) -> Callable[[], IBuilder]:
        def _factory():
            return GenericBuilder(name)

        return _factory


@dataclass
class Builders:
    context: IBuilder = field(default_factory=GenericBuilder.factory("context"))
    key_store: IBuilder = field(default_factory=GenericBuilder.factory("key store"))
    clients: IBuilder = field(default_factory=GenericBuilder.factory("host client"))


class ClientException(Exception):
    def __init__(self, message):
        super(ClientException, self).__init__(message)


class IFileAccess(ABC):
    def get(self) -> bytes:
        pass

    def put(self, value: bytes):
        pass
