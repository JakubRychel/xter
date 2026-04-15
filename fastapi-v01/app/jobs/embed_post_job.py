from dataclasses import dataclass
from fastapi.app.jobs.base_job import BaseJob

@dataclass
class EmbedPostJob(BaseJob):
    post_id: int
    post_content: str
    thread_content: str