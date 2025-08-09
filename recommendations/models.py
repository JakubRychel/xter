from django.db import models
from django.contrib.auth import get_user_model
from pgvector.django import VectorField

User = get_user_model()

class InteractionEmbedding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    embedding = VectorField(dimensions=512)
    label = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    used_in_model = models.BooleanField(default=False)

class GlobalRecommendationModel(models.Model):
    name = models.CharField(max_length=50)
    model = models.FileField(upload_to='models_storage/global/')

class UserRecommendationModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    model = models.FileField(upload_to='models_storage/users/')