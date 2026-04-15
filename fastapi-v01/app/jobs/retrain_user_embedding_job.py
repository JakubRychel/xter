from dataclasses import dataclass
from fastapi.app.jobs.base_job import BaseJob

@dataclass(slots=True)
class RetrainUserEmbeddingJob(BaseJob):
    user_id: int
    post_id: int
    alpha: float
    raw: str | None = None