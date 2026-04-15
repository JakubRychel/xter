from fastapi import APIRouter, Depends
from app.schemas.embeddings_schema import CreatePostEmbeddingsJob, RetrainUserEmbeddingJob
from app.services.embeddings_service import PostEmbeddingsService, UserEmbeddingsService

router = APIRouter(prefix='/embeddings', tags=['embeddings'])

@router.post('/posts/embed')
async def create_post_embeddings(
    job: CreatePostEmbeddingsJob,
    service: PostEmbeddingsService = Depends()
):
    await service.handle_request(job)

    return {'status': 'ok'}

@router.post('/users/retrain')
async def retrain_user_embedding(
    job: RetrainUserEmbeddingJob,
    service: UserEmbeddingsService = Depends()
):
    await service.handle_request(job)

    return {'status': 'ok'}



@router.get('/posts/all')
async def get_all_post_embeddings():
    from app.core.qdrant import qdrant_client
    
    points = qdrant_client.scroll(
        collection_name='posts',
        limit=100,
        with_payload=True,
        with_vectors=True
    )

    return points

@router.get('/posts/{post_id}')
async def get_post_embeddings(post_id: int):
    from app.core.qdrant import qdrant_client
    
    points = qdrant_client.retrieve(
        collection_name='posts',
        ids=[post_id],
        with_payload=True,
        with_vectors=True
    )

    return points

@router.get('/users/all')
async def get_all_user_embeddings():
    from app.core.qdrant import qdrant_client
    
    points = qdrant_client.scroll(
        collection_name='users',
        limit=100,
        with_payload=True,
        with_vectors=True
    )

    return points

@router.get('/users/{user_id}')
async def get_user_embedding(user_id: int):
    from app.core.qdrant import qdrant_client
    
    points = qdrant_client.retrieve(
        collection_name='users',
        ids=[user_id],
        with_payload=True,
        with_vectors=True
    )

    return points

@router.delete('/delete')
async def delete_collections():
    from app.core.qdrant import qdrant_client
    
    qdrant_client.delete_collection('posts')
    qdrant_client.delete_collection('users')

    return {'status': 'ok'}