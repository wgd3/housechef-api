from faker import Faker
from datetime import timedelta
from housechef.database.models import Meal, Recipe, Household, MealRecipe

from sqlalchemy import not_

fake = Faker()


def create_meal_history_for_household(household_id: int, days: int = 7):
    household = Household.get_by_id(household_id)

    create_meal_for_date = lambda dt: Meal.create(date=dt, household_id=household_id)

    # create one meal per day for X days
    for (dt, meal) in fake.time_series(
        start_date=f"-{days}d",
        end_date="now",
        precision=timedelta(days=1),
        distrib=create_meal_for_date,
    ):
        print(f"Created meal {meal.id} for date {dt} in household {household.name}")
        recipe = find_unique_recipe(household)
        meal.recipes.append(recipe)
        meal.save()


def find_unique_recipe(household: Household) -> Recipe:
    meals_so_far = [
        m.id for m in Meal.query.filter(Meal.household_id == household.id).all()
    ]
    used_recipes = [
        r.recipe_id
        for r in MealRecipe.query.filter(MealRecipe.meal_id.in_(meals_so_far))
    ]
    remaining_recipes = [
        r.id for r in Recipe.query.filter(not_(Recipe.id.in_(used_recipes)))
    ]
    if len(remaining_recipes) == 0:
        return Recipe.query.first()
    return Recipe.get_by_id(remaining_recipes.pop())
