import pytest

from posts.models import Post


@pytest.mark.django_db
def test_set_mentioned_users(user_factory):
    author = user_factory(username='author')
    john = user_factory(username='john')
    alice = user_factory(username='alice')
    bob = user_factory(username='bob')

    post = Post.create(author=author, content='Hello @john, @mark and @alice')

    mentioned_users = set(post.mentioned_users.values_list('username', flat=True))

    assert mentioned_users == {'john', 'alice'}
    assert 'bob' not in mentioned_users
    assert 'mark' not in mentioned_users