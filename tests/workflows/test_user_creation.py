from sqlalchemy.exc import IntegrityError

from housechef.database.models import User, Household


def test_user_creation_without_household(db, user_factory):
    try:
        User.create(
            username="testuser", email="noreply@housechef.io", password="testuser"
        )
    except IntegrityError as ie:
        assert ie is not None


def test_user_creation_with_household(db):
    household = Household.create(name="test house")
    user = User.create(
        username="testuser",
        email="noreply@housechef.io",
        password="testuser",
        household_id=household.id,
    )
    assert user.active == True
    assert user.household.name == "test house"
