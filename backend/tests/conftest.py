import pytest

from tests.factories.users import UserFactory


@pytest.fixture
def user_factory():
    return UserFactory