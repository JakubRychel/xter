from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_db: int = 4

    qdrant_host: str = 'localhost'
    qdrant_port: int = 6333
    qdrant_api_key: str = Field(..., env='QDRANT_API_KEY')

    embeddings_model: str = 'sentence-transformers/all-MiniLM-L6-v2'
    embeddings_vector_size: int = 384

    genai_model: str = 'gemini-2.5-flash-lite'
    gemini_api_key: str = Field(..., env='GEMINI_API_KEY')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()