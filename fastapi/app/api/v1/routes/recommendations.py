from datetime import timedelta

from fastapi import APIRouter, Depends
from app.schemas.recommendations_schema import RecommendationsRequest, RecommednationsResponse
from app.services.recommendations_service import RecommendationsService

router = APIRouter(prefix='/recommendations', tags=['recommendations'])

@router.post('/get', response_model=RecommednationsResponse)
async def get_recommended_posts(
    payload: RecommendationsRequest,
    service: RecommendationsService = Depends()
):
    posts = await service.get_recommended_posts(
        payload.user_id,
        payload.limit,
        timedelta(**payload.delta.model_dump(exclude_none=True))
    )

    return {'recommended_posts': posts}