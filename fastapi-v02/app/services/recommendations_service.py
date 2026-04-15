from app.repositories.qdrant_repo import QdrantRepo

class RecommendationsService:
    def __init__(self):
        self.qdrant = QdrantRepo()

    async def get_recommended_posts(self, user_id: int, limit: int, delta: dict[str, int]) -> dict[int, float]:
        user_embedding = self.qdrant.get_user_embeddings([user_id])[user_id]
        recommended_posts = self.qdrant.get_recommended_posts(user_embedding, limit, delta)

        return recommended_posts