from housechef.database.models import User, Recipe


def test_create_user(db, user_factory):
    user = user_factory.create()

    db.session.add(user)
    db.session.commit()

    assert user.active is True
    assert user.time_updated is None
