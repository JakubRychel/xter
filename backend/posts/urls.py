from django.urls import path, include
from .views import PostViewSet
from adrf.routers import DefaultRouter

router = DefaultRouter()
router.register(r'posts', PostViewSet)

urlpatterns = [
    path('', include(router.urls))
]