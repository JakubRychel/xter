from itertools import chain
from heapq import nlargest
from app.repositories.qdrant_repo import QdrantRepo

class RecommendationsService:
    def __init__(self):
        self.qdrant = QdrantRepo()

    async def get_recommended_posts(self, user_id: int, limit: int):
        posts, threads = await self.qdrant.get_recommendations(user_id, limit)

        scores = {}

        for id, score in chain(posts.items(), threads.items()):
            if score > scores.get(id, 0):
                scores[id] = score

        sorted_scores = dict(nlargest(limit, scores.items(), key=lambda x: x[1]))

        return sorted_scores