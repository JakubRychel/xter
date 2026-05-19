from adrf import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from .models import Post
from .serializers import PostSerializer
from recommendations.logic import get_recommendations, refill_recommendations
from django.db.models import Case, IntegerField, When
from datetime import datetime, timezone

class PostPagePagination(PageNumberPagination):
    page_size = 25

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostPagePagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        parent_id = request.query_params.get('parent_id')
        author = request.query_params.get('author')
        followed = request.query_params.get('followed')

        if author is not None:
            queryset = Post.objects.filter(author__username=author).order_by('-published_at')

        elif parent_id is not None:
            queryset = Post.objects.filter(parent_id=parent_id).order_by('-published_at')
        
        elif followed is not None and followed.lower() == 'true':
            queryset = Post.objects.filter(author__in=self.request.user.followed_users.all()).order_by('-published_at')
        
        else:
            queryset = Post.objects.all().order_by('-published_at')

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)
  
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    async def live_feed(self, request):
        from common.redis_client import get_aredis
        redis = get_aredis()

        user_id = request.user.id
        page = request.query_params.get('page')

        if page is not None:
            page = int(page)

        page_size = self.pagination_class.page_size

        FEED = f'feed:v1:feed:{user_id}'
        SEEN = f'feed:v1:seen:{user_id}'
        META = f'feed:v1:meta:{user_id}'

        snapshot_exists = False #await redis.exists(FEED)

        if not snapshot_exists:
            timestamp = int(datetime.now(timezone.utc).timestamp())

            await redis.hset(META, 'timestamp', timestamp)
            await redis.expire(META, 3600)

            recommendations = await get_recommendations(user_id)

            if recommendations:
                await redis.zadd(FEED, recommendations)
                await redis.expire(FEED, 3600)

        elif page is None:
            seen_ids = await redis.smembers(SEEN)

            if seen_ids:
                pipe = redis.pipeline()

                for post_id in seen_ids:
                    score = await redis.zscore(FEED, post_id)

                    if score is not None and float(score) > 1:
                        pipe.zincrby(FEED, -1, post_id)

                pipe.delete(SEEN)
                await pipe.execute()

            timestamp = int(await redis.hget(META, 'timestamp'))

            new_recommendations = await refill_recommendations(user_id, limit=page_size, timestamp=timestamp)
            
            new_timestamp = int(datetime.now(timezone.utc).timestamp())

            await redis.hset(META, 'timestamp', new_timestamp)
            await redis.expire(META, 3600)

            if new_recommendations:
                await redis.zadd(FEED, new_recommendations)
                await redis.expire(FEED, 3600)

        start = (int(page) - 1) * page_size if page is not None else 0
        end = start + page_size - 1

        post_ids = await redis.zrevrange(FEED, start, end)

        if not post_ids:
            queryset = Post.objects.all().order_by('-published_at')

            page_content = await self.apaginate_queryset(queryset)

            if page_content is not None:
                serializer = self.get_serializer(page_content, many=True)

                return await self.get_apaginated_response(await serializer.adata)
            
            serializer = self.get_serializer(queryset, many=True)

            return Response(await serializer.adata)

        post_ids = [int(post_id) for post_id in post_ids]
        
        await redis.sadd(SEEN, *post_ids)
        await redis.expire(SEEN, 3600)

        ordering = Case(
            *[
                When(id=post_id, then=position)
                for position, post_id in enumerate(post_ids)
            ],
            output_field=IntegerField()
        )

        queryset = (
            Post.objects
            .select_related('author')
            .filter(id__in=post_ids)
            .order_by(ordering, '-published_at')
        )

        serializer = self.get_serializer(queryset, many=True)

        count = await redis.zcard(FEED)

        has_next = end + 1 < count
        has_previous = start > 0

        if not page:
            page = 1

        all = await redis.zrevrange(FEED, 0, -1, withscores=True)
        #print(all, count)

        return Response({
            'count': count,
            'next': page + 1 if has_next else None,
            'previous': page -1 if has_previous else None,
            'results': await serializer.adata
        })
    

    def perform_create(self, serializer):
        serializer.instance = Post.create(author=self.request.user, **serializer.validated_data)

    def perform_update(self, serializer):
        post = self.get_object()

        if post.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('You can edit only your own post.')
        
        if serializer.validated_data.get('parent', post.parent) != post.parent:
            raise PermissionDenied('You cannot change the parent of a reply.')

        instance = serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('You can delete only your own post.')
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        success = post.like(request.user)

        if not success:
            return Response(
                {'detail': 'Post already liked.'},
                status=400
            )

        return Response({'status': 'post_liked'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        success = post.unlike(request.user)

        if not success:
            return Response(
                {'detail': 'Post was not liked.'},
                status=400
            )

        return Response({'status': 'post_unliked'})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def read(self, request, pk=None):
        post = self.get_object()
        post.read_by.add(request.user)

        return Response({'status': 'post_read'})