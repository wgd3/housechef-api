import pytest

from housechef.database.models import User, Recipe


@pytest.mark.usefixtures("db")
class TestUserCreation:
    def test_create_user(self, db, user_factory):
        user = user_factory.create()

        db.session.add(user)
        db.session.commit()

        assert user.active is True
        assert user.time_updated is None
        assert len(user.roles) == 1
