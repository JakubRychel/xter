

from datetime import timedelta

from app.repositories.qdrant_repo import QdrantRepo


class RecommendationsService:
    def __init__(self):
        self.qdrant = QdrantRepo()

    async def get_recommended_posts(
        self,
        user_id: int,
        limit: int,
        delta: timedelta
    ) -> dict[int, float]:
        recommended_posts = await self.qdrant.get_recommendations(user_id, limit, delta)

        return recommended_posts


