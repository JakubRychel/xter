from django.db import models
from django.db.models import F, Case, When, Value, BooleanField


HOT_THRESHOLD = 1

class PostMetrics(models.Model):
    post = models.OneToOneField('posts.Post', on_delete=models.CASCADE, related_name='metrics')

    has_embeddings = models.BooleanField(default=False)

    likes_count = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0)

    popularity = models.FloatField(default=0, db_index=True)
    is_hot = models.BooleanField(default=False, db_index=True)

    published_at = models.DateTimeField(blank=True, null=True, db_index=True)

    def handle_like(self):
        type(self).objects.filter(id=self.id).update(
            likes_count=F('likes_count') + 1,
            popularity=F('popularity') + 1,
            is_hot=Case(
                When(
                    popularity__gte=HOT_THRESHOLD - 1,
                    then=Value(True)
                ),
                default=F('is_hot'),
                output_field=BooleanField()
            )
        )

        print('liked')

    def handle_unlike(self):
        type(self).objects.filter(id=self.id).update(
            likes_count=F('likes_count') - 1,
            popularity=F('popularity') - 1,
            is_hot=Case(
                When(
                    popularity__lt=HOT_THRESHOLD + 1,
                    then=Value(False)
                ),
                default=F('is_hot'),
                output_field=BooleanField()
            )
        )

        print('unliked')

    def handle_create_reply(self):
        type(self).objects.filter(id=self.id).update(
            replies_count=F('replies_count') + 1,
            popularity=F('popularity') + 3,
            is_hot=Case(
                When(
                    popularity__gte=HOT_THRESHOLD - 3,
                    then=Value(True)
                ),
                default=F('is_hot'),
                output_field=BooleanField()
            )
        )

        print('reply')

    def handle_delete_reply(self):
        type(self).objects.filter(id=self.id).update(
            replies_count=F('replies_count') - 1,
            popularity=F('popularity') - 3,
            is_hot=Case(
                When(
                    popularity__lt=HOT_THRESHOLD + 3,
                    then=Value(False)
                ),
                default=F('is_hot'),
                output_field=BooleanField()
            )
        )