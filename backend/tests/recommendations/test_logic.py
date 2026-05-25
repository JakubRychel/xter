import pytest
from django.contrib.auth import get_user_model

from posts.models import Post
from recommendations.logic import collect_thread

User = get_user_model()


@pytest.fixture
def user(db):
    user = User.objects.create()

    return user


@pytest.mark.django_db
def test_collect_thread_returns_posts_in_correct_order(user):
    root = Post.objects.create(
        author=user,
        content='root'
    )

    reply_1 = Post.objects.create(
        author=user,
        content='reply 1',
        parent=root
    )

    reply_2 = Post.objects.create(
        author=user,
        content='reply 2',
        parent=reply_1
    )

    posts = collect_thread(reply_2.id)

    contents = [post.content for post in posts]

    assert contents == [
        'root',
        'reply 1',
        'reply 2'
    ]