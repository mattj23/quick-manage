from abc import ABC
from dataclasses import dataclass
from typing import List, Optional, Dict, Callable, TextIO


@dataclass
class FileInfo:
    directory: str
    file_name: str
    last_modified: float
    size: int
    check_sum: Optional[str] = None


class IFileProvider(ABC):
    """ Abstract base class encapsulating all operations which interact with the file system. """

    def mkdirs(self, path: str):
        raise NotImplementedError()

    def chmod(self, path: str, permissions: int):
        pass

    def get_all(self, path: str, predicate: Optional[Callable[[str], bool]] = None) -> List[FileInfo]:
        raise NotImplementedError()

    def read_file(self, path: str) -> TextIO:
        raise NotImplementedError()

    def write_file(self, path: str) -> TextIO:
        raise NotImplementedError()

    def checksum(self, path: str) -> str:
        raise NotImplementedError()

    def move_file(self, source: str, dest: str):
        raise NotImplementedError()

    def exists(self, path: str) -> bool:
        raise NotImplementedError()

    def remove(self, path: str):
        raise NotImplementedError()
