import pytest

from tests.factories.users import UserFactory
from tests.factories.posts import PostFactory


@pytest.fixture
def user_factory():
    return UserFactory

@pytest.fixture
def post_factory():
    return PostFactory