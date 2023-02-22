from __future__ import annotations

import os
import shutil

from .impl_helpers import to_yaml, from_yaml
from ._common import EntityConfig
from dataclasses import dataclass, asdict, field

import click
from typing import Optional, List, Tuple, Dict, Union

APPLICATION_NAME = "quick-manage"
CONFIG_FOLDER = click.get_app_dir(APPLICATION_NAME)


@dataclass
class Style:
    fg: Optional[str] = None
    bg: Optional[str] = None
    bold: Optional[bool] = None
    underline: Optional[bool] = None
    blink: Optional[bool] = None
    reverse: Optional[bool] = None

    def __call__(self, text, **kwargs) -> str:
        d = asdict(self)
        d.update(kwargs)
        return click.style(text, **d)

    def echo(self, text, nl=True):
        click.echo(self(text), nl=nl)

    def display_attributes(self) -> List[str]:
        return sorted(f"{k}={v}" for k, v in asdict(self).items())

    @staticmethod
    def default_warning() -> Style:
        return Style(fg="yellow")

    @staticmethod
    def default_success() -> Style:
        return Style(fg="green", bold=True)

    @staticmethod
    def default_fail() -> Style:
        return Style(fg="red", bold=True)

    @staticmethod
    def default_visible() -> Style:
        return Style(fg="bright_blue")

    @staticmethod
    def default_head() -> Style:
        return Style(bold=True, underline=True)


@dataclass
class Styles:
    warning: Style = field(default_factory=Style.default_warning)
    success: Style = field(default_factory=Style.default_success)
    fail: Style = field(default_factory=Style.default_fail)
    visible: Style = field(default_factory=Style.default_visible)
    head: Style = field(default_factory=Style.default_head)

    def to_display_list(self) -> List[Tuple[str, str, Style]]:
        return [
            ("warning", "Style for text that highlights problems or issues", self.warning),
            ("fail", "Style for text that shows when an operation has failed", self.fail),
            ("success", "Style for text that shows a success condition", self.success),
            ("visible", "Style for text that should be visible or highlighted in a way that draws attention to it, but"
                        " is not necessarily good or bad", self.visible),
        ]


@dataclass
class QuickConfig:
    active_context: Optional[str] = None
    styles: Styles = field(default_factory=Styles)
    contexts: List[EntityConfig] = field(default_factory=list)

    def write(self, file_name: str):
        with open(file_name, "w") as handle:
            to_yaml(self, handle)

    @staticmethod
    def load(file_name: str) -> QuickConfig:
        with open(file_name, "r") as handle:
            return from_yaml(QuickConfig, handle)

    @staticmethod
    def _new_with_defaults() -> QuickConfig:
        config = QuickConfig()
        context_folder = os.path.join(CONFIG_FOLDER, "local-context")
        config.contexts.append(EntityConfig("local", "filesystem", {"path": context_folder}))
        config.active_context = "local"
        return config

    @staticmethod
    def default() -> QuickConfig:
        config_file = os.path.join(CONFIG_FOLDER, "config.yaml")

        if not os.path.exists(CONFIG_FOLDER):
            os.makedirs(CONFIG_FOLDER)

        if not os.path.exists(config_file):
            config = QuickConfig._new_with_defaults()
            config.write(config_file)

        return QuickConfig.load(config_file)
