from pathlib import Path
import json
import pickle
from typing import (
    MutableSet,
    TypeVar,
    Optional,
    Set,
    MutableMapping,
    Dict,
    Iterator,
    MutableSequence,
    List,
)
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


class PersistSequence(MutableSequence[T]):
    def __init__(self, file_name: str, default: Optional[List[T]] = None, **kwargs):
        self.data = default or []
        if kwargs:
            self.data.update(kwargs)
        self.file_path = Path(f".data/{file_name}.pkl")
        if self.file_path.exists():
            try:
                with self.file_path.open("rb") as f:
                    self.data.extend(pickle.load(f))
            except (IOError, ValueError):
                _logger.log(
                    logging.WARNING, f"Could not load data from {self.file_path}"
                )
        else:
            _logger.info(f"Creating new file {self.file_path}")

    def __getitem__(self, i: int) -> T:
        return self.data[i]

    def __setitem__(self, i: int, x: T) -> None:
        self.data[i] = x

    def __delitem__(self, i: int) -> None:
        del self.data[i]

    def __len__(self) -> int:
        return len(self.data)

    def insert(self, i: int, x: T) -> None:
        self.data.insert(i, x)

    def save(self) -> None:
        with self.file_path.open("wb") as f:
            pickle.dump(self.data, f)


KT = TypeVar("KT")
VT = TypeVar("VT")


class PersistMapping(MutableMapping[KT, VT]):
    # Cannot get type argument at runtime https://stackoverflow.com/questions/57706180/generict-base-class-how-to-get-type-of-t-from-within-instance
    def __init__(
        self,
        filename: str,
        default: Optional[Dict[KT, VT]] = None,
        **kwargs,
    ) -> None:
        self.data = default if default is not None else {}
        if kwargs:
            self.update(kwargs)
        self.file_path = Path(f".data/{filename}.json")
        if self.file_path.exists():
            try:
                with self.file_path.open("rb") as f:
                    self.data.update(json.load(f))
            except (IOError, ValueError):
                _logger.log(logging.WARN, f"Error loading {self.file_path} cache")
        else:
            _logger.info(f"Created new {self.file_path} cache")

    def __contains__(self, key: KT) -> bool:
        return key in self.data

    def __delitem__(self, key: KT) -> None:
        del self.data[key]

    def __getitem__(self, key: KT) -> VT:
        if key in self.data:
            return self.data[key]
        raise KeyError(key)

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[KT]:
        return iter(self.data)

    def __setitem__(self, key: KT, value: VT) -> None:
        self.data[key] = value

    def update(self, other=(), /, **kwds) -> None:
        """Updates the dictionary from an iterable or mapping object."""
        if isinstance(other, abc.Mapping):
            for key in other:
                self.data[key] = other[key]
        elif hasattr(other, "keys"):
            for key in other.keys():
                self.data[key] = other[key]
        else:
            for key, value in other:
                self.data[key] = value
        for key, value in kwds.items():
            self.data[key] = value

    def save_to_disk(self) -> None:
        with self.file_path.open("wb") as f:
            json.dump(self.data, f)
