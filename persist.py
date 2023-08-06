from pathlib import Path
import json
from typing import MutableSet, TypeVar, Optional, Set
import logging

_logger = logging.getLogger(__name__)

T = TypeVar("T")


# https://stackoverflow.com/a/64323140/7552308
class PersistSet(MutableSet[T]):
    def __init__(self, file_name: str, default: Optional[Set[T]] = None, **kwargs):
        self.data = default or set()
        if kwargs:
            self.data.update(kwargs)
        self.file_path = Path(f".data/{file_name}.json")
        if self.file_path.exists():
            try:
                with self.file_path.open("rb") as f:
                    self.data.update(json.load(f))
            except (IOError, ValueError):
                _logger.log(
                    logging.WARNING, f"Could not load data from {self.file_path}"
                )
        else:
            _logger.info(f"Creating new file {self.file_path}")

    def __contains__(self, x: object) -> bool:
        return super().__contains__(x)

    def __iter__(self):
        return super().__iter__()

    def __len__(self) -> int:
        return super().__len__()

    def add(self, x: T) -> None:
        self.data.add(x)

    def discard(self, x: T) -> None:
        self.data.discard(x)

    def update(self, x: Set[T]) -> None:
        self.data.update(x)
