from .conftest import client

async def get_post_scores(user_id: int, post_ids: list[int]) -> dict[int, float]:
    return {post_id: 0.5 for post_id in post_ids}

