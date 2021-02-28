def test_create_meal(db, meal_factory, user_factory, recipe_factory):
    user = user_factory.create()
    recipes = recipe_factory.create_batch(3)
    meal = meal_factory.create(user=user)

    db.session.add(meal)
    db.session.commit()

    for r in recipes:
        r.meal_id = meal.id
        db.session.add(r)

    db.session.commit()

    assert meal.user_id == user.id
    # assert len(meal.recipes) == 3
