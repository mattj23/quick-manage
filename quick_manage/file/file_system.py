import os
from typing import List, Optional, Callable, TextIO
from ._common import IFileProvider, FileInfo
import hashlib
import shutil


class FileSystem(IFileProvider):
    """ Concrete implementation of a cross-platform FileSystemProvider based on Python's os and shutil module. """

    def remove(self, path: str):
        os.remove(path)

    def __init__(self, *args, **kwargs):
        pass

    def mkdirs(self, path: str):
        os.makedirs(path)

    def get_all(self, path: str, predicate: Optional[Callable[[str], bool]] = None) -> List[FileInfo]:
        predicate = (lambda x: True) if predicate is None else predicate
        results = []
        for root, dirs, files in os.walk(path):
            for f in filter(predicate, files):
                file_path = os.path.abspath(os.path.join(root, f))
                directory, file_name = os.path.split(file_path)
                modified = os.path.getmtime(file_path)
                size = os.path.getsize(file_path)
                results.append(FileInfo(directory, file_name, modified, size))

        return results

    def chmod(self, path: str, permissions: int):
        os.chmod(path, 0o700)

    def read_file(self, path: str) -> TextIO:
        return open(path, "r")

    def write_file(self, path: str) -> TextIO:
        folder = os.path.dirname(os.path.abspath(path))
        if not os.path.exists(folder):
            os.makedirs(folder)
        return open(path, "w")

    def checksum(self, path: str) -> str:
        sha = hashlib.sha1()
        with open(path, "rb") as handle:
            while True:
                data = handle.read(65536)
                if not data:
                    break
                sha.update(data)
        return sha.hexdigest()

    def move_file(self, source: str, dest: str):
        if os.path.exists(dest):
            raise FileExistsError(f"The file {dest} already exists! Aborting rather than overwrite")
        shutil.move(source, dest)

    def exists(self, path: str) -> bool:
        return os.path.exists(path)
