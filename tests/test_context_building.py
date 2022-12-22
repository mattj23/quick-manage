import pytest
from quick_manage._common import EntityConfig, Builders
from quick_manage.context.local_file_context import LocalFileContext
from quick_manage.keys import FileStore
from quick_manage.serialization import to_yaml_string
from tests.tools.file_mocks import TestFileSystemProvider


def test_local_file_context_build():
    builders = Builders()
    builders.context.register("filesystem", LocalFileContext, LocalFileContext.Config)

    config = EntityConfig("local", "filesystem", {"path": "/test/path"})
    context = builders.context.build(config, builders=builders)
    assert isinstance(context, LocalFileContext)
    assert isinstance(context.config, LocalFileContext.Config)
    assert context.config.path == "/test/path"
    assert context._builders == builders


def test_local_file_context_key_stores():
    # Fake file system
    config = EntityConfig("local", "filesystem", {"path": "/test/path"})
    key_config = LocalFileContext.KeyStoresConfig()
    key_config.stores.append(EntityConfig("local", "folder", {"path": "/test/path/local-keys"}))
    key_config.stores.append(EntityConfig("local1", "folder", {"path": "/test/path/local-keys1"}))
    key_config.default_store = "local"
    contents = {
        "/test/path/key-stores.yaml": dict(modified=1234, content=to_yaml_string(key_config)),
        "/test/path/local-keys/test-secret": dict(modified=2345, content="123456"),
        "/test/path/local-keys/test-secret2": dict(modified=3456, content="6543210")
    }

    mock_file_system = TestFileSystemProvider(contents)

    builders = Builders()
    extra = dict(file_system=mock_file_system)
    builders.context.register("filesystem", LocalFileContext, LocalFileContext.Config, extra)
    builders.key_store.register("folder", FileStore, FileStore.Config, extra)

    context = builders.context.build(config, builders=builders)
    assert isinstance(context, LocalFileContext)

    key_store = context.key_stores["local"]
    assert key_store.get("test-secret") == "123456"
    assert "test-secret2" in key_store.list()
