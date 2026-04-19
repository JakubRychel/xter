from datetime import timedelta

from fastapi import APIRouter, Depends
from app.schemas.recommendations_schema import RecommendationsRequest, RecommednationsResponse, ScoreRequest, ScoreResponse
from app.services.recommendations_service import RecommendationsService

router = APIRouter(prefix='/recommendations', tags=['recommendations'])

@router.post('/get', response_model=RecommednationsResponse)
async def get_recommended_posts(
    payload: RecommendationsRequest,
    service: RecommendationsService = Depends()
):
    delta = timedelta(**payload.delta.model_dump(exclude_none=True))

    posts = await service.get_recommended_posts(
        payload.user_id,
        payload.limit,
        delta
    )

    return {'recommended_posts': posts}

@router.post('/score', response_model=ScoreResponse)
async def get_thread_score(
    payload: ScoreRequest,
    service: RecommendationsService = Depends()
):
    score = await service.get_thread_score(
        payload.bot_id,
        payload.post_id
    )

    return {'score': score}
