from django.core.management.base import BaseCommand
from django.db.models import Count
from ...models import PostMetrics
from posts.models import Post


def update_metrics_counts():
    posts = (
        Post.objects
        .annotate(
            calculated_replies_count=Count('replies', distinct=True),
            calculated_likes_count=Count('liked_by', distinct=True)
        )
    )

    metrics = [
        PostMetrics(
            post=post,
            replies_count=post.calculated_replies_count,
            likes_count=post.calculated_likes_count,
            published_at=post.published_at
        )
        for post in posts
    ]

    PostMetrics.objects.bulk_create(
        metrics,
        update_conflicts=True,
        update_fields=['replies_count', 'likes_count'],
        unique_fields=['post']
    )

class Command(BaseCommand):
    help = 'Update replies_count, likes_count and dislikes_count for all post metrics'

    def handle(self, *args, **options):
        update_metrics_counts()
        self.stdout.write(self.style.SUCCESS('Successfully updated metrics counts.'))