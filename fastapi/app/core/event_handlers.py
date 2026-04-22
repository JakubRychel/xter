async def handle_post_embeddings_created(*post_ids):
    from app.services.embeddings_service import UserEmbeddingsService

    print(f'event handler: {post_ids}')

    service = UserEmbeddingsService()
    await service.launch(*post_ids)