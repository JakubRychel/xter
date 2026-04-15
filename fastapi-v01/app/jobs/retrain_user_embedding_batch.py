from app.jobs.base_batch import BaseBatch
from app.jobs.retrain_user_embedding_job import RetrainUserEmbeddingJob

class RetrainUserEmbeddingBatch(BaseBatch[RetrainUserEmbeddingJob]):
    job_class = RetrainUserEmbeddingJob

