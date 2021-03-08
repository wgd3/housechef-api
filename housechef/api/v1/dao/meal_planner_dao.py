import datetime as dt
import random
from housechef.database.models import Meal, Recipe, MealRecipe, Household

from flask import current_app

from sqlalchemy import or_, func, and_, not_


class MealPlannerDAO(object):
    """DAO for providing users with suggestions for their next meal"""

    @staticmethod
    def suggest_recipe_for_meal(meal: Meal, day_threshold: int = 7) -> Recipe:
        """
        Method for evaluating all recipes available to a household, and returning one based on a number of factors.

        TODO: Consider dietary restrictions (DietType)
        TODO: Evaluate if meal already has main/side (DishType)
        TODO: Consider nutritional information for all users in a household

        Args:
            meal:

        Returns:
            object:

        """
        household = meal.household

        # seven days ago
        oldest_date = dt.date.today() - dt.timedelta(days=day_threshold)

        # get list of meals in last 7 days
        meals_in_range = Meal.query.filter(
            and_(
                func.DATE(Meal.date) > oldest_date,
                func.DATE(Meal.date) <= dt.date.today(),
            )
        ).all()

        # and ignore any recipes cooked in those meals
        ignore_recipes = MealRecipe.query.filter(
            MealRecipe.meal_id.in_([m.id for m in meals_in_range])
        ).all()

        # find recipe not in ignored list
        available_recipes = Recipe.query.filter(
            and_(
                not_(Recipe.id.in_([ri.recipe_id for ri in ignore_recipes])),
                or_(Recipe.household_id == household.id, Recipe.household_id == None),
            )
        ).all()

        selected = available_recipes[random.randint(0, len(available_recipes) - 1)]
        current_app.logger.debug(
            f"Suggesting recipe '{selected.name}' for meal on {meal.date}"
        )
        return selected

    @staticmethod
    def suggest_meal_for_date(
        date: dt.date, household: Household, side_dish_count=0
    ) -> Meal:
        """
        Method for crafting meals based on multiple attributes
        Args:
            side_dish_count:
            household:
            date:

        Returns:

        """
        return None
