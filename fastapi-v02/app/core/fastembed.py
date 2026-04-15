from fastembed import TextEmbedding
from .config import settings

embedder = TextEmbedding(
    model_name=settings.embeddings_model,
    lazy_load=True
)