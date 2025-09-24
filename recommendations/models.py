from django.db import models
from django.contrib.auth import get_user_model
from pgvector.django import VectorField

User = get_user_model()

class GlobalEmbedding(models.Model):
    name = models.CharField(max_length=50)
    embedding = VectorField(dimensions=512)
    created_at = models.DateTimeField(auto_now_add=True)

class PostEmbedding(models.Model):
    post = models.OneToOneField('posts.Post', on_delete=models.CASCADE, related_name='embedding')
    embedding = VectorField(dimensions=512)
    created_at = models.DateTimeField(auto_now_add=True)

class UserEmbedding(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='embedding')
    embedding = VectorField(dimensions=512)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PreservedUserRecommendations(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preserved_recommendations')
    post_ids = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Interaction(models.Model):
    embedding = models.ForeignKey('PostEmbedding', on_delete=models.CASCADE, related_name='interactions')
    label = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    used_in_model = models.BooleanField(default=False)

class GlobalRecommendationModel(models.Model):
    name = models.CharField(max_length=50)
    model = models.FileField(upload_to='models_storage/global/')

class UserRecommendationModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    model = models.FileField(upload_to='models_storage/users/')