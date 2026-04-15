from pydantic import BaseModel

class BaseJob(BaseModel):
    job_id: int | None = None

class CreatePostEmbeddingsJob(BaseJob):
    post_id: int
    timestamp: int
    post_content: str
    thread_content: str | None = None

class RetrainUserEmbeddingJob(BaseJob):
    user_id: int
    post_id: int
    alpha: float