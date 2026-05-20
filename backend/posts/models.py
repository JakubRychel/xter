import re
from django.db import models, transaction, IntegrityError
from django.db.models import F
from recommendations.models import PostMetrics

class Post(models.Model):
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='posts')

    liked_by = models.ManyToManyField('users.User', related_name='liked_posts', blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    disliked_by = models.ManyToManyField('users.User', related_name='disliked_posts', blank=True)
    dislikes_count = models.PositiveIntegerField(default=0)

    read_by = models.ManyToManyField('users.User', related_name='read_posts', blank=True)
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True, db_index=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')

    replies_count = models.PositiveBigIntegerField(default=0)

    mentioned_users = models.ManyToManyField('users.User', related_name='mentions', blank=True)

    embeddings_created = models.BooleanField(default=False)

    def set_mentioned_users(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        pattern = re.compile(r'@([\w.@+-]*[\w])\b')
        usernames = set(pattern.findall(self.content))

        if not usernames:
            self.mentioned_users.clear()
            return
        
        mentioned_users = User.objects.filter(username__in=usernames)
        self.mentioned_users.set(mentioned_users)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.set_mentioned_users()

    def like(self, user_id):
        through = self.liked_by.through

        try:
            with transaction.atomic():
                through.objects.create(
                    post_id=self.id,
                    user_id=user_id
                )

            type(self).objects.filter(id=self.id).update(likes_count=F('likes_count') + 1)

            self.metrics.handle_like()

            return True

        except IntegrityError:
            return False

    def unlike(self, user_id):
        through = self.liked_by.through

        with transaction.atomic():
            deleted, _ = through.objects.filter(
                post_id=self.id,
                user_id=user_id
            ).delete()

            if not deleted:
                return False
            
            type(self).objects.filter(id=self.id).update(likes_count=F('likes_count') - 1)

            self.metrics.handle_unlike()

            return True
        
    def increment_replies_count(self):
        type(self).objects.filter(id=self.id).update(replies_count=F('replies_count') + 1)

    @classmethod
    def create(cls, author, content, parent=None, **kwargs):
        with transaction.atomic():
            post = cls.objects.create(
                author=author,
                content=content,
                parent=parent,
                **kwargs
            )

            PostMetrics.objects.create(
                post=post,
                published_at=post.published_at
            )

            if parent:
                parent.increment_replies_count()
                parent.metrics.handle_create_reply()

            return post
        
    def delete(self):
        with transaction.atomic():
            parent = self.parent

            if parent:
                parent.metrics.handle_delete_reply()

            self.delete()