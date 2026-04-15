from dataclasses import dataclass
from abc import ABC
import json

from app.repositories.redis_repo import get_next_job_id, get_timestamp

@dataclass(slots=True)
class BaseJob(ABC):
    @classmethod
    def create(cls, payload: dict):
        job_id = get_next_job_id()
        timestamp = get_timestamp()

        return cls(payload, job_id=job_id, timestamp=timestamp)