from datetime import timedelta

from app.core.qdrant import qdrant_client
from app.repositories.qdrant_repo import QdrantRepo


class RecommendationsService:
    def __init__(self):
        self.qdrant = QdrantRepo(qdrant_client)

    async def get_recommended_posts(
        self,
        user_id: int,
        chunks: list[tuple[int, tuple[timedelta | None, timedelta | None]]]
    ) -> dict[int, float]:
        scored_posts = await self.qdrant.get_recommendations(user_id, chunks)

        return scored_posts

    async def get_post_scores(
        self,
        user_id: int,
        post_ids: list[int]
    ) -> dict[int, float]:
        scored_posts = await self.qdrant.get_post_scores(user_id, post_ids)

        return scored_posts

    async def get_thread_score_for_bot(
        self,
        bot_id: int,
        post_id: int
    ) -> float:
        score = await self.qdrant.get_thread_score_for_bot(bot_id, post_id)

        return score