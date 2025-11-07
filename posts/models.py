from django.db import models
import re

class Post(models.Model):
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='posts')
    liked_by = models.ManyToManyField('users.User', related_name='liked_posts', blank=True)
    read_by = models.ManyToManyField('users.User', related_name='read_posts', blank=True)
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')

    mentioned_users = models.ManyToManyField('users.User', related_name='mentions', blank=True)

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
