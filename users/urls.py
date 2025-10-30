from django.urls import path, include
from .views import RegisterView, UserDetailView, UserViewSet, CustomTokenObtainPairView, CustomTokenRefreshView, LogoutView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/current-user/', UserDetailView.as_view(), name='current_user'),
]