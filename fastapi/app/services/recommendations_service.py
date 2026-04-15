

class RecommendationsService:
    def __init__(self):
        pass

    async def get_recommended_posts(
        self,
        user_id: int,
        limit: int,
        delta: int
    ) -> dict[int, float]:
        print('received')