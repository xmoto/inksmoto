import tempfile
import os.path
from pathlib import Path


def mkdir_recursive(path: str | Path):
    if not isinstance(path, Path):
        path = Path(path)
    path.mkdir(parents=True, exist_ok=True)


def create_parent_dirs(path: str | Path):
    dir_path = os.path.dirname(path)
    if not os.path.isdir(dir_path):
        mkdir_recursive(dir_path)


def tmpdir() -> str:
    return tempfile.gettempdir()


def first_existing_path[T: Path | str](paths: list[T]) -> T | None:
    return next((path for path in paths if os.path.exists(path)), None)
