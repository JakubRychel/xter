from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

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