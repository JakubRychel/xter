from datetime import timedelta

from app.repositories.qdrant_repo import QdrantRepo


class RecommendationsService:
    def __init__(self):
        self.qdrant = QdrantRepo()

    async def get_recommended_posts(
        self,
        user_id: int,
        chunks: list[tuple[int, tuple[timedelta | None, timedelta | None]]]
    ) -> dict[int, float]:
        recommended_posts = await self.qdrant.get_recommendations(user_id, chunks)

        return recommended_posts

    async def get_thread_score(
        self,
        bot_id: int,
        post_id: int
    ) -> float:
        score = await self.qdrant.get_thread_score(bot_id, post_id)

        return score

