import os
import io
import hashlib
from copy import deepcopy
from typing import TextIO, Optional, Callable, List, Dict, Tuple

from quick_manage.file import IFileProvider, FileInfo


class StringWrapper(io.StringIO):
    def __init__(self, on_close: Callable[[str], None]):
        super().__init__()
        self.on_close = on_close

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.on_close(self.getvalue())
        super().__exit__(exc_type, exc_val, exc_tb)


class TestFileSystemProvider(IFileProvider):
    """
        Mock for FileSystemProvider that operates on an in memory python dictionary.  The dictionary should
        be formatted as follows and given to the provider on initialization.

        {
            "<file path 1>": {
                "content": "this is the content of the file",
                "modified": 1234
                },
            "<file path 2>": { ... }
        }

    """

    def __init__(self, internal: Dict):
        self.internal = internal

    def checksum(self, path: str) -> str:
        raise NotImplementedError()

    def remove(self, path: str):
        if path in self.internal:
            del self.internal[path]

    def mkdirs(self, path: str):
        pass

    def get_all(self, path: str, predicate: Optional[Callable[[str], bool]] = None) -> List[FileInfo]:
        def _check(s: str) -> bool:
            if predicate is None:
                return s.startswith(path)
            else:
                return s.startswith(path) and predicate(s)

        results = []
        for k, v in self.internal.items():
            if _check(k):
                directory, name = os.path.split(k)
                info = FileInfo(directory, name, v["modified"], len(v["content"]))
                results.append(info)

        return results

    def write_file(self, path) -> TextIO:
        if path not in self.internal:
            self.internal[path] = {}

        def write_action(s: str):
            self.internal[path]["content"] = s

        return StringWrapper(write_action)

    def read_file(self, path) -> TextIO:
        return io.StringIO(self.internal[path]["content"])

    def move_file(self, source: str, dest: str):
        self.internal[dest] = deepcopy(self.internal[source])
        del self.internal[source]

    def exists(self, path: str) -> bool:
        return path in self.internal
