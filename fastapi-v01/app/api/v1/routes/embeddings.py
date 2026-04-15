from fastapi import APIRouter, Depends
from app.schemas.embeddings_schema import GeneratePostEmbeddingsRequest, RetrainUserEmbeddingRequest
from app.services.embeddings_service import PostEmbeddingService, UserEmbeddingService

router = APIRouter(prefix='/embeddings', tags=['embeddings'])

@router.post('/posts/generate')
async def generate_post_embedding(
    payload: GeneratePostEmbeddingsRequest,
    service: PostEmbeddingService = Depends()
):
    await service.handle_generate_embedding_request(
        payload.post_id,
        payload.post_content,
        payload.thread_content or None
    )

    return {'status': 'ok'}

@router.post('/users/retrain')
async def retrain_user_embedding(
    payload: RetrainUserEmbeddingRequest,
    service: UserEmbeddingService = Depends()
):
    await service.handle_retrain_request(
        payload.user_id,
        payload.post_id,
        payload.alpha
    )

    return {'status': 'ok'}