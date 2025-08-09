from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    followed_users = models.ManyToManyField('self', related_name='followers', symmetrical=False, blank=True)
    is_bot = models.BooleanField(default=False)
    displayed_name = models.CharField(max_length=80, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)