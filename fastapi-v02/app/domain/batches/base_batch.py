from app.repositories.redis_repo import RedisRepo
from app.domain.jobs.base_job import BaseJob
from pydantic import BaseModel, PrivateAttr
from typing import List, Generic, Iterator, ClassVar, TypeVar

T = TypeVar('T', bound='BaseJob')

class BaseBatch(BaseModel, Generic[T]):
    jobs: List[T] = []

    namespace: ClassVar[str]
    
    _redis: RedisRepo = PrivateAttr()

    def model_post_init(self):
        self._redis = RedisRepo(namespace=self.namespace)

    def __iter__(self) -> Iterator[T]:
        return iter(self.jobs)
    
    def __len__(self) -> int:
        return len(self.jobs)
    
    def __getitem__(self, index: int) -> T:
        return self.jobs[index]
    
    def __bool__(self) -> bool:
        return bool(self.jobs)
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(size={len(self)})'