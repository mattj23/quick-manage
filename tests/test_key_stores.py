import pytest
from quick_manage.keys import Secret, IKeyStore


def test_valid_names():
    assert Secret.name_is_valid("tH.is_-/is/val1d_")
    assert not Secret.name_is_valid("-tH.is_-/is/val1d_")
    assert not Secret.name_is_valid("tH.is_-/is/val1d_.")
    assert not Secret.name_is_valid("tH.is_-/is/val1d_-")
    assert not Secret.name_is_valid("/tH.is_-/is/val1d_")
    assert not Secret.name_is_valid("tH.is_-/is/val1d_/")


def test_secret_name_validation():
    with pytest.raises(ValueError):
        value = Secret(".start/this")


