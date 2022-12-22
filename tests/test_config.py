import pytest
import io
from quick_manage.serialization import to_yaml, from_yaml
from quick_manage.config import Style, Styles, EntityConfig, QuickConfig


def test_default_styles():
    styles = Styles()
    assert styles.warning == Style.default_warning()
    assert styles.success == Style.default_success()
    assert styles.fail == Style.default_fail()
    assert styles.visible == Style.default_visible()


def test_default_styles_are_mutable():
    styles0 = Styles()
    styles1 = Styles()
    styles0.warning.blink = True
    assert styles0.warning != Style.default_warning()
    assert styles0.warning.blink
    assert not styles1.warning.blink


def test_styles_serialize_round_trip():
    styles = Styles()
    styles.warning.blink = True
    styles.success.bg = "purple"
    stream = io.StringIO()
    to_yaml(styles, stream)

    stream.seek(0)
    loaded = from_yaml(Styles, stream)

    assert styles == loaded


def test_create_config():
    config = QuickConfig()
    config.contexts.append(EntityConfig("local", "filesystem", {"path": "local_folder"}))
    config.active_context = "local"
    stream = io.StringIO()
    to_yaml(config, stream)

    stream.seek(0)
    loaded = from_yaml(QuickConfig, stream)
    assert loaded == config

