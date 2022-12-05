from __future__ import annotations

import os
import shutil
import yaml

import click
from typing import Optional, List, Tuple, Dict

APPLICATION_NAME = "quick-manage"
CONFIG_FOLDER = click.get_app_dir(APPLICATION_NAME)


class Style:
    def __init__(self, **kwargs):
        if kwargs is None:
            kwargs = {}

        self.fg: Optional[str] = kwargs.get("fg", None)
        self.bg: Optional[str] = kwargs.get("bg", None)
        self.bold: Optional[bool] = kwargs.get("bold", None)
        self.underline: Optional[bool] = kwargs.get("underline", None)
        self.blink: Optional[bool] = kwargs.get("blink", None)
        self.reverse: Optional[bool] = kwargs.get("reverse", None)

    def as_dict(self):
        return self.__dict__

    def __call__(self, text, **kwargs) -> str:
        d = dict(self.as_dict())
        d.update(kwargs)
        return click.style(text, **self.as_dict())

    def echo(self, text, nl=True):
        click.echo(self(text), nl=nl)

    def display_attributes(self) -> List[str]:
        return sorted(f"{k}={v}" for k, v in self.as_dict().items())


class Styles:
    def __init__(self, **kwargs):
        self.warning = Style(**kwargs.get("warning", dict(fg="yellow")))
        self.success = Style(**kwargs.get("success", dict(fg="green", bold=True)))
        self.fail = Style(**kwargs.get("fail", dict(fg="red", bold=True)))
        self.visible = Style(**kwargs.get("visible", dict(fg="bright_blue")))

        self.map = {
            "warning": self.warning,
            "fail": self.fail,
            "success": self.success,
            "visible": self.visible
        }

        self.packed = (self.warning, self.fail, self.success, self.visible)

    def to_display_list(self) -> List[Tuple[str, str, Style]]:
        return [
            ("warning", "Style for text that highlights problems or issues", self.warning),
            ("fail", "Style for text that shows when an operation has failed", self.fail),
            ("success", "Style for text that shows a success condition", self.success),
            ("visible", "Style for text that should be visible or highlighted in a way that draws attention to it, but"
                        " is not necessarily good or bad", self.visible),
        ]

    def to_serializable(self):
        return {k: v.as_dict() for k, v in self.map.items()}


class Config:
    def __init__(self, **kwargs):
        self.file: str = kwargs.get("file")

        style_config: Dict = kwargs.get("styles", {})
        self.styles = Styles(**style_config)

        self.key_stores: Dict = kwargs.get("key_stores", {"local": {"type": "config-folder", "default": True}})
        self.certs: Dict = kwargs.get("certs", dict())
        self.hosts: Dict = kwargs.get("hosts", dict())

    def write(self):
        data = {
            "styles": self.styles.to_serializable(),
            "key_stores": self.key_stores,
            "certs": self.certs,
            "hosts": self.hosts,
        }

        if os.path.exists(self.file):
            shutil.copy(self.file, self.file + ".back")
        with open(self.file, "w") as handle:
            yaml.dump(data, handle)

    @staticmethod
    def load(file_path: str) -> Config:
        with open(file_path, "r") as handle:
            try:
                kwargs = yaml.safe_load(handle)
                kwargs["file"] = file_path
                return Config(**kwargs)
            except:
                click.echo(click.style(f"The configuration file {file_path} could not be loaded/parsed", bold=True,
                                       fg="bright_red"))
                raise


def load_config() -> Config:
    config_file = os.path.join(CONFIG_FOLDER, "config.yaml")

    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)

    if not os.path.exists(config_file):
        config = Config(file=config_file)
        config.write()

    return Config.load(config_file)
