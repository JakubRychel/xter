from fastapi import APIRouter, Depends
from app.schemas.recommendations_schema import RecommendedPostsRequest, RecommendedPostsResponse
from app.services.recommendations_service import RecommendationsService

router = APIRouter(prefix='/recommendations', tags=['recommendations'])

@router.get('/posts', response_model=RecommendedPostsResponse)
async def get_recommended_posts(
    payload: RecommendedPostsRequest,
    service: RecommendationsService = Depends()
):
    posts = await service.get_recommended_posts(payload.user_id, payload.limit, payload.delta)

    return {'recommended_posts': posts}