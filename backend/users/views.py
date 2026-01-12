from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.decorators import action
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegisterSerializer, UserSerializer, EditProfileSerializer, ChangePasswordSerializer


User = get_user_model()


class LogoutView(APIView):
    def post(self, request):
        response = Response({'detail': 'Logged out successfully.'})

        response.delete_cookie(key='refresh', path='/api/auth/token/refresh/', samesite='Lax')

        return response

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.get('refresh')

        if refresh_token:
            response.set_cookie(
                key='refresh',
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/api/auth/token/refresh/',
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
            )

            del response.data['refresh']

        return response
    
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')

        if not refresh_token:
            return Response({'detail': 'Refresh token not provided in cookies.'}, status=401)
        
        serializer = self.get_serializer(data={'refresh': refresh_token})
        serializer.is_valid(raise_exception=True)

        access_token = serializer.validated_data.get('access')
        new_refresh_token = serializer.validated_data.get('refresh', None)

        response = Response({'access': access_token})

        if new_refresh_token:
            response.set_cookie(
                key='refresh',
                value=new_refresh_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/api/auth/token/refresh/',
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
            )

        return response

class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class EditProfileView(generics.UpdateAPIView):
    serializer_class = EditProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    lookup_field = 'username'
    lookup_url_kwarg = 'username'

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def follow(self, request, username=None):
        request_user = request.user
        user_to_follow = self.get_object()

        request_user.followed_users.add(user_to_follow)

        return Response({'status': 'user_followed'})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unfollow(self, request, username=None):
        request_user = request.user
        user_to_unfollow = self.get_object()

        request_user.followed_users.remove(user_to_unfollow)

        return Response({'status': 'user_unfollowed'})
