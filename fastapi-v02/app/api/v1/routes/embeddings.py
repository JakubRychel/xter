from fastapi import APIRouter, Depends
from app.domain.jobs.create_post_embeddings_job import CreatePostEmbeddingsJob
from app.domain.jobs.retrain_user_embedding_job import RetrainUserEmbeddingJob
from app.services.embeddings_service import PostEmbeddingsService, UserEmbeddingService
from app.repositories.qdrant_repo import QdrantRepo

router = APIRouter(prefix='/embeddings', tags=['embeddings'])

@router.post('/posts/embed')
async def generate_post_embedding(
    job: CreatePostEmbeddingsJob,
    service: PostEmbeddingsService = Depends()
):
    await service.handle_request(job)

    return {'status': 'ok'}

@router.post('/users/retrain')
async def retrain_user_embedding(
    job: RetrainUserEmbeddingJob,
    service: UserEmbeddingService = Depends()
):
    await service.handle_request(job)

    return {'status': 'ok'}





@router.get('/users/all')
async def fetch_all_user_embeddings(
    repo: QdrantRepo = Depends()
):
    embeddings = await repo.fetch_all_user_embeddings()
    
    return {'embeddings': embeddings}

@router.get('/users/{user_id}')
async def fetch_user_embedding(
    user_id: int,
    repo: QdrantRepo = Depends()
):
    embedding = await repo.fetch_user_embedding(user_id)
    
    if embedding is None:
        return {'error': 'User embedding not found'}
    
    return {
        'user_id': user_id,
        'embedding': embedding
    }

@router.get('/posts/all')
async def fetch_all_post_embeddings(
    repo: QdrantRepo = Depends()
):
    embeddings = await repo.fetch_all_post_embeddings()
    
    return {'embeddings': embeddings}

@router.get('/posts/{post_id}')
async def fetch_post_embeddings(
    post_id: int,
    repo: QdrantRepo = Depends()
):
    post_embedding, thread_embedding = await repo.fetch_post_embeddings(post_id)
    
    if post_embedding is None:
        return {'error': 'Post embedding not found'}
    
    return {
        'post_id': post_id,
        'post_embedding': post_embedding,
        'thread_embedding': thread_embedding
    }