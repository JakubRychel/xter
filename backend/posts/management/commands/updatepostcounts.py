from django.core.management.base import BaseCommand
from django.db.models import Count
from ...models import Post


def updatepostcounts():
    posts = Post.objects.annotate(
        calculated_replies_count=Count('replies', distinct=True),
        calculated_likes_count=Count('liked_by', distinct=True),
        calculated_dislikes_count=Count('disliked_by', distinct=True)
    )

    updates = []

    for post in posts:
        updates.append(
            Post(id=post.id, replies_count=post.calculated_replies_count, likes_count=post.calculated_likes_count, dislikes_count=post.calculated_dislikes_count)
        )

    Post.objects.bulk_update(updates, ['replies_count', 'likes_count', 'dislikes_count'])

class Command(BaseCommand):
    help = 'Update replies_count, likes_count and dislikes_count for all posts'

    def handle(self, *args, **options):
        update_post_counts()
        self.stdout.write(self.style.SUCCESS('Successfully updated post counts.'))