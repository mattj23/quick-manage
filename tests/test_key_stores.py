import pytest
from quick_manage.keys import Secret, IKeyStore
from quick_manage.file import FolderKeyStore
from quick_manage.impl_helpers import sha1_digest

from tests.tools.file_mocks import TestFileSystemProvider


def test_valid_names():
    assert Secret.name_is_valid("tH.i-s_/is/val1d_")
    assert not Secret.name_is_valid("-tH.is_/is/val1d_")
    assert not Secret.name_is_valid("tH.is_/is/val1d_.")
    assert not Secret.name_is_valid("tH.is_/is/val1d_-")
    assert not Secret.name_is_valid("/tH.is_/is/val1d_")
    assert not Secret.name_is_valid("tH.is_/is/val1d_/")


def test_secret_name_validation():
    with pytest.raises(ValueError):
        value = Secret(".start/this")


def test_folder_store_create():
    payload = "this is test data"

    mock_fs = TestFileSystemProvider({})
    store = FolderKeyStore(FolderKeyStore.Config("/test"), file_system=mock_fs)
    store.put_value("secret0", None, payload)

    assert store.get_value("secret0", None) == payload


def test_folder_store_persists():
    payload = "this is test data"

    mock_fs = TestFileSystemProvider({})
    store = FolderKeyStore(FolderKeyStore.Config("/test"), file_system=mock_fs)
    store.put_value("secret0", None, payload)

    new_store = FolderKeyStore(FolderKeyStore.Config("/test"), file_system=mock_fs)
    assert new_store.get_value("secret0", None) == payload


def test_folder_store_two_keys():
    payload0 = "this is test data"
    payload1 = "this is different test data"

    mock_fs = TestFileSystemProvider({})
    store = FolderKeyStore(FolderKeyStore.Config("/test"), file_system=mock_fs)
    store.put_value("secret0", "test0", payload0)
    store.put_value("secret0", "test1", payload1)

    assert store.get_value("secret0", "test0") == payload0
    assert store.get_value("secret0", "test1") == payload1


def test_folder_store_delete_one_removes_secret():
    payload = "this is test data"

    mock_fs = TestFileSystemProvider({})
    store = FolderKeyStore(FolderKeyStore.Config("/test"), file_system=mock_fs)
    store.put_value("secret0", "test", payload)
    assert store.get_value("secret0", "test") == payload

    store.rm("secret0", "test")
    with pytest.raises(KeyError):
        store.get_value("secret0", "test")


def test_folder_store_delete_one_key_leaves_other():
    payload0 = "this is test data"
    payload1 = "this is different test data"

    mock_fs = TestFileSystemProvider({})
    store = FolderKeyStore(FolderKeyStore.Config("/test"), file_system=mock_fs)
    store.put_value("secret0", "test0", payload0)
    store.put_value("secret0", "test1", payload1)

    store.rm("secret0", "test0")
    assert store.get_value("secret0", "test1") == payload1
    with pytest.raises(KeyError):
        store.get_value("secret0", "test")


def test_folder_store_no_delete_on_identical_secret():
    payload = "this is test data"

    mock_fs = TestFileSystemProvider({})
    store = FolderKeyStore(FolderKeyStore.Config("/test"), file_system=mock_fs)
    store.put_value("secret0", None, payload)
    store.put_value("secret1", None, payload)

    store.rm("secret0", None)
    assert store.get_value("secret1", None) == payload
    with pytest.raises(KeyError):
        store.get_value("secret0", None)
