from app.repositories.redis_repo import RedisRepo
from app.repositories.qdrant_repo import QdrantRepo
from pydantic import BaseModel, PrivateAttr
from typing import ClassVar

class BaseJob(BaseModel):
    _redis: ClassVar['RedisRepo']
    _qdrant: ClassVar['QdrantRepo']