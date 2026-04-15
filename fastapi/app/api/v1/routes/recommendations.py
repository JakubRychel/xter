from fastapi import APIRouter, Depends
from app.schemas.recommendations_schema import RecommendationsRequest, RecommednationsResponse
from app.services.recommendations_service import RecommendationsService

router = APIRouter(prefix='/recommendations', tags=['recommendations'])

@router.get('/get', response_model=RecommednationsResponse)
async def get_recommended_posts(
    payload: RecommendationsRequest,
    service: RecommendationsService = Depends()
):
    posts = await service.get_recommended_posts(
        payload.user_id,
        payload.limit,
        payload.delta
    )

    return {'recommended_posts': posts}