from django.core.management.base import BaseCommand
from ...tasks import create_post_embeddings_task
from posts.models import Post


class Command(BaseCommand):
    help = 'Create post embeddings for all posts that do not have them yet'

    def handle(self, *args, **options):
        post_ids = Post.objects.filter(embeddings_created=False).values_list('id', flat=True)

        if not post_ids:
            self.stdout.write(self.style.SUCCESS('All post embeddings are already created.'))
            return

        for post_id in post_ids:
            create_post_embeddings_task.delay(post_id)

        self.stdout.write(self.style.SUCCESS(f'Enqueued embedding creation for {len(post_ids)} posts.'))
