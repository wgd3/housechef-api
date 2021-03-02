from housechef.database.models import Recipe, User, Note


def test_create_recipe(app, recipe_factory):
    recipe = recipe_factory.create()

    # just make sure the factory worked as intended
    assert recipe.servings >= 1

    # make sure directions are returned as a list
    assert isinstance(recipe.directions, list)


def test_create_recipe_with_user(db, recipe_factory, household_factory):
    household = household_factory.create()

    db.session.add(household)
    db.session.commit()

    recipe = recipe_factory.create(household=household)
    # recipe.submitted_by = user

    db.session.add(recipe)
    db.session.commit()

    assert recipe.household_id == household.id
    assert len(household.recipes) == 1
