from housechef.extensions import db
from housechef.database.models import User, Household


def test_new_household(app, db, household_factory):
    household = household_factory.create()

    db.session.add(household)
    db.session.commit()

    assert household.id >= 0


def test_add_user_to_household(db, household_factory, user_factory):
    household = household_factory.create()
    user = user_factory.create()

    db.session.add(household)
    db.session.add(user)
    db.session.commit()

    household.users.append(user)
    household.save()

    assert user.id in [user.id for user in household.users]
