import pytest

from posts.models import Post


@pytest.mark.django_db
def test_set_mentioned_users(user_factory, post_factory):
    author = user_factory(username='author')
    john = user_factory(username='john')
    alice = user_factory(username='alice')
    bob = user_factory(username='bob')

    post = post_factory(author=author, content='Hello @john, @mark and @alice')

    mentioned_users = set(post.mentioned_users.values_list('username', flat=True))

    assert mentioned_users == {'john', 'alice'}
    assert 'bob' not in mentioned_users
    assert 'mark' not in mentioned_users

@pytest.mark.django_db
def test_set_mentioned_users_clears_mentions(user_factory, post_factory):
    author = user_factory(username='author')
    john = user_factory(username='john')

    post = post_factory(author=author, content='Hello @john')

    assert post.mentioned_users.count() == 1

    post.content = 'No mentions'
    post.save()

    post.refresh_from_db()

    assert post.mentioned_users.count() == 0

@pytest.mark.django_db
def test_like_adds_like(user_factory, post_factory):
    author = user_factory()
    liker = user_factory()

    post = post_factory(author=author)

    result = post.like(liker.id)

    post.refresh_from_db()

    assert result is True
    assert post.likes_count == 1
    assert post.liked_by.filter(id=liker.id).exists()

@pytest.mark.django_db
def test_like_prevents_duplicates(user_factory, post_factory):
    author = user_factory()
    liker = user_factory()

    post = post_factory(author=author)

    assert post.like(liker.id) is True
    assert post.like(liker.id) is False

    post.refresh_from_db()

    assert post.likes_count == 1

@pytest.mark.django_db
def test_unlike_removes_like(user_factory, post_factory):
    author = user_factory()
    liker = user_factory()

    post = post_factory(author=author)

    post.like(liker.id)

    result = post.unlike(liker.id)

    post.refresh_from_db()

    assert result is True
    assert post.likes_count == 0

    assert not post.liked_by.filter(id=liker.id).exists()

@pytest.mark.django_db
def test_unlike_without_like_does_not_decrement_likes_count(user_factory, post_factory):
    author = user_factory()
    liker = user_factory()
    unliker = user_factory()

    post = post_factory(author=author)

    result = post.like(liker.id)

    post.refresh_from_db()

    assert result is True
    assert post.likes_count == 1

    result = post.unlike(unliker.id)

    post.refresh_from_db()

    assert result is False
    assert post.likes_count == 1

@pytest.mark.django_db
def test_create_creates_metrics(user_factory, post_factory):
    author = user_factory()

    post = post_factory(author=author)

    assert post.id is not None
    assert hasattr(post, 'metrics')

@pytest.mark.django_db
def test_reply_increments_parent_reply_count(user_factory, post_factory):
    author = user_factory()

    parent = post_factory(author=author)

    post_factory(author=author, parent=parent)

    parent.refresh_from_db()

    assert parent.replies_count == 1

@pytest.mark.django_db
def test_delete_reply_decrements_parent_reply_count(user_factory, post_factory):
    author = user_factory()

    parent = post_factory(author=author)

    reply = post_factory(author=author, parent=parent)

    parent.refresh_from_db()

    assert parent.replies_count == 1

    reply.delete()

    parent.refresh_from_db()

    assert parent.replies_count == 0

@pytest.mark.django_db
def test_post_without_parent(user_factory, post_factory):
    author = user_factory()

    post = post_factory(author=author)

    assert post.parent is None
    assert post.replies_count == 0