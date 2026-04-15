from pydantic import BaseModel

class RecommendationsRequest(BaseModel):
    user_id: int
    limit: int = 5000
    delta: dict[str, int] = {'days': 100}

class RecommednationsResponse(BaseModel):
    recommended_posts: dict[int, float]