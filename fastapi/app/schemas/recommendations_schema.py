from pydantic import BaseModel

class TimeRange(BaseModel):
    start: dict | None = None
    end: dict | None = None

class RecommendationChunk(BaseModel):
    limit: int = 5000
    time_range: TimeRange | None = None

class RecommendationsRequest(BaseModel):
    user_id: int
    chunks: list[RecommendationChunk]

class RecommednationsResponse(BaseModel):
    recommended_posts: dict[int, float]

class ScoreRequest(BaseModel):
    bot_id: int
    post_id: int

class ScoreResponse(BaseModel):
    score: float