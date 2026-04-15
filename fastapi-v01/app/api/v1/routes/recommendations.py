from fastapi import APIRouter, Depends
from app.schemas.recommendations_schema import RecommendedPostsResponse
from app.services.recommendations_service import RecommendationService

router = APIRouter(prefix='/recommendations', tags=['recommendations'])

@router.get('/posts', response_model=RecommendedPostsResponse)
async def get_recommended_posts(
    user_id: str,
    limit: int=5000,
    service: RecommendationService = Depends()
):
    posts = await service.get_recommended_posts(user_id, limit)

    return {'recommended_posts': posts}