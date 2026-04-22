def create_embeddings_for_all_posts():
    from recommendations.services import create_post_embeddings_request
    from recommendations.logic import collect_thread

    for post in Post.objects.all().iterator():
        try:
            create_post_embeddings_request(
                post_id=post.id,
                timestamp=int(post.published_at.timestamp()),
                post_content=post.content,
                thread_content='\n\n'.join(collect_thread(post.id).values_list('content', flat=True))
            )
            print(f"OK: {post.id}")

        except Exception as e:
            print(f"ERROR: {post.id} -> {e}")