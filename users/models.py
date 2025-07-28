from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    followed_users = models.ManyToManyField('self', related_name='followers', blank=True)