from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from .models import Post
from .serializers import PostSerializer
from recommendations.logic import get_recommended_posts, retrain_user_embedding

class PostPagePagination(PageNumberPagination):
    page_size = 10

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostPagePagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.action == 'list':
            parent_id = self.request.query_params.get('parent_id')
            author = self.request.query_params.get('author')
            followed = self.request.query_params.get('followed')

            if author is not None:
                return Post.objects.filter(author__username=author).order_by('-published_at')

            if parent_id is not None:
                return Post.objects.filter(parent_id=parent_id).order_by('-published_at')
            
            if followed is not None and followed.lower() == 'true':
                return Post.objects.filter(author__in=self.request.user.followed_users.all()).order_by('-published_at')

            if self.request.user.is_authenticated:
                recommended_posts = get_recommended_posts(self.request.user)

                return list(recommended_posts.exclude(read_by=self.request.user)) + list(recommended_posts.filter(read_by=self.request.user))
        
        return Post.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save(author=self.request.user)

        if instance.parent:
            retrain_user_embedding(self.request.user, 'reply', instance.parent.id)
        else:
            retrain_user_embedding(self.request.user, 'post', instance.id)

    def perform_update(self, serializer):
        post = self.get_object()
        if post.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('You can edit only your own post.')
        
        if serializer.validated_data.get('parent', post.parent) != post.parent:
            raise PermissionDenied('You cannot change the parent of a reply.')

        instance = serializer.save()

        if instance.parent:
            retrain_user_embedding(self.request.user, 'reply', instance.parent.id)
        else:
            retrain_user_embedding(self.request.user, 'post', instance.id)

    def perform_destroy(self, instance):
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('You can delete only your own post.')
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        post.liked_by.add(request.user)

        retrain_user_embedding(request.user, 'like', post.id)

        return Response({'status': 'post_liked'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        post.liked_by.remove(request.user)

        retrain_user_embedding(request.user, 'unlike', post.id)

        return Response({'status': 'post_unliked'})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def read(self, request, pk=None):
        post = self.get_object()
        post.read_by.add(request.user)

        return Response({'status': 'post_read'})