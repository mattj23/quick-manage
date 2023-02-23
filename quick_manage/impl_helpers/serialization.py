"""
    Serialization tools
"""
from io import StringIO
from typing import Dict, Union

import ruamel.yaml as yaml
from dataclasses import asdict as _as_dict
from dacite import from_dict
from typing.io import TextIO


def as_dict_strip(obj) -> Dict:
    return _as_dict(obj, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})


def to_yaml(obj, target: Union[TextIO, StringIO, str]):
    if isinstance(target, str):
        with open(target, "w") as handle:
            yaml.dump(as_dict_strip(obj), handle)
    else:
        yaml.dump(as_dict_strip(obj), target)


def to_yaml_string(obj) -> str:
    target = StringIO()
    to_yaml(obj, target)
    target.seek(0)
    return target.read()


def from_yaml(data_cls, target: Union[TextIO, StringIO, str]):
    return from_dict(data_cls, yaml.load(target, Loader=yaml.Loader))
