import datetime as dt
from housechef.database.models import User, Recipe, Household, Meal, MealRecipe


def test_create_meal_without_recipes(db, household_factory):
    household = Household.create(name="test")
    meal = Meal.create(date=dt.date.today(), recipes=[], household_id=household.id)

    assert meal.id is not None
    assert meal.household_id == household.id


def test_create_meal_with_recipes(db, household_factory):
    household = Household.create(name="test")
    recipe = Recipe.create(name="test")
    meal = Meal.create(date=dt.date.today(), household_id=household.id)

    # test adding via association proxy
    meal.recipes.append(recipe)
    meal.save()

    assert len(meal.recipes) == 1

    # test adding MealRecipe directly
    recipe = Recipe.create(name="meal_recipe_test")
    meal.meal_recipes.append(MealRecipe(recipe, meal))
    meal.save()
    assert len(meal.recipes) == 2


def test_all_house_users_can_see_meals(db):
    household = Household.create(name="test")

    user1 = User.create(
        username="user1",
        email="noreply1@housechef.io",
        password="user1",
        household_id=household.id,
    )
    user2 = User.create(
        username="user2",
        email="noreply2@housechef.io",
        password="user2",
        household_id=household.id,
    )

    recipe = Recipe.create(name="test")
    meal = Meal.create(date=dt.date.today(), household_id=household.id)
    meal.recipes.append(recipe)

    # make sure household -> meals -> recipes are all tied together
    assert len(meal.recipes) == 1
    assert len(household.meals) == 1

    # make sure both users can see the meal
    assert len(user1.household.meals) == 1
    assert len(user2.household.meals) == 1

    assert user1.household.meals[0].recipes[0] == user2.household.meals[0].recipes[0]
