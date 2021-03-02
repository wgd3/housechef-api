def test_create_meal(db, meal_factory, household_factory, recipe_factory):
    household = household_factory.create()
    recipes = recipe_factory.create_batch(3)
    meal = meal_factory.create(household=household)

    db.session.add(meal)
    db.session.commit()

    for r in recipes:
        r.meal_id = meal.id
        db.session.add(r)

    db.session.commit()

    assert meal.household_id == household.id
    # assert len(meal.recipes) == 3
