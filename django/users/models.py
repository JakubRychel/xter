from django.db import models
from django.contrib.auth.models import AbstractUser
from pathlib import Path
import uuid

def profile_pictures_path(instance, filename):
    return f'profile_pictures/{uuid.uuid4()}{Path(filename).suffix}'

class User(AbstractUser):
    followed_users = models.ManyToManyField('self', related_name='followers', symmetrical=False, blank=True)
    is_bot = models.BooleanField(default=False)

    displayed_name = models.CharField(max_length=80, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    profile_picture = models.ImageField(upload_to=profile_pictures_path, null=True, blank=True)

    gender = models.CharField(
        max_length=6,
        choices=[
            ('male', 'Male'),
            ('female', 'Female')
        ],
        null=True,
        blank=True
    )