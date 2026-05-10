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
    posts = await service.get_recommended_posts(
        payload.user_id,
        [(
            chunk.limit,
            (
                timedelta(**chunk.time_range.start) if chunk.time_range and chunk.time_range.start else None,
                timedelta(**chunk.time_range.end) if chunk.time_range and chunk.time_range.end else None
            )
        ) for chunk in payload.chunks]
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
