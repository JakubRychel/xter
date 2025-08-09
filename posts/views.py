from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import CursorPagination
from .models import Post
from .serializers import PostSerializer
from recommendations.logic import register_like_or_post, register_unlike, register_reply, get_recommended_posts

class PostCursorPagination(CursorPagination):
    page_size = 10
    ordering = '-published_at'

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostCursorPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        parent_id = self.request.query_params.get('parent_id')

        if parent_id is not None:
            return Post.objects.filter(parent_id=parent_id).order_by('-published_at')

        return get_recommended_posts(self.request.user)

    def perform_create(self, serializer):
        instance = serializer.save(author=self.request.user)

        register_like_or_post(self.request.user, instance.content)

        if instance.parent is not None:
            register_reply(self.request.user, instance.parent.content, instance.content)

    def perform_destroy(self, instance):
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('You can delete only your own post.')
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        post.likes.add(request.user)

        register_like_or_post(request.user, post.content)

        return Response({'status': 'post_liked'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        post.likes.remove(request.user)

        register_unlike(request.user, post.content)

        return Response({'status': 'post_unliked'})