import pytest
from quick_manage._common import EntityConfig, Builders
from quick_manage.context.local_file_context import LocalFileContext
from quick_manage.keys import FileStore
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

