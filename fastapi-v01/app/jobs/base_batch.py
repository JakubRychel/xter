from collections.abc import Sequence, Iterator
from typing import TypeVar, Generic

T = TypeVar('T')

class BaseBatch(Sequence, Generic[T]):
    __slots__ = ('_jobs',)

    def __init__(self, jobs: list[T] | tuple[T, ...]):
        self._jobs: tuple[T, ...] = tuple(jobs)

    def __iter__(self) -> Iterator[T]:
        return iter(self._jobs)
    
    def __len__(self) -> int:
        return len(self._jobs)
    
    def __getitem__(self, index: int) -> T:
        return self._jobs[index]
    
    def __bool__(self) -> bool:
        return bool(self._jobs)
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(size={len(self)})'