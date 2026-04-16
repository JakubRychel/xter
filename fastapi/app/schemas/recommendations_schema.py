from pydantic import BaseModel

class Delta(BaseModel):
    days: int | None = None
    hours: int | None = None
    minutes: int | None = None

class RecommendationsRequest(BaseModel):
    user_id: int
    limit: int = 5000
    delta: Delta = Delta(days=100)

class RecommednationsResponse(BaseModel):
    recommended_posts: dict[int, float]