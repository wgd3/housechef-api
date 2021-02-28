from housechef.database.models import User, Recipe


def test_create_user(db, user_factory):
    # user = User.create(
    #     username="testuser", email="testuser@mail.com", password="testuser"
    # )
    user = user_factory.create()

    db.session.add(user)
    db.session.commit()

    assert user.active is True
    assert user.time_updated is None
    assert len(user.recipes) == 0


def test_add_recipe_to_user(db, user_factory, recipe_factory):
    user = user_factory.create()
    db.session.add(user)
    db.session.commit()

    recipe = recipe_factory.create()
    db.session.add(recipe)
    db.session.commit()

    user.recipes.append(recipe)
    db.session.commit()

    assert len(user.recipes) == 1
