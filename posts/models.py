from django.db import models

class Post(models.Model):
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='posts')
    liked_by = models.ManyToManyField('users.User', related_name='liked_posts', blank=True)
    read_by = models.ManyToManyField('users.User', related_name='read_posts', blank=True)
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')