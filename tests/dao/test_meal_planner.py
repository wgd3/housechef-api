import pytest
import random
import datetime as dt
from housechef.api.v1.dao import MealPlannerDAO
from housechef.database.models import Meal


@pytest.mark.usefixtures("db", "meal_factory", "household_factory", "recipe_factory")
class TestMealPlannerRecipeSuggestion:
    def setup(self):
        pass

    def test_get_recipe_suggestion(
        self, db, meal_factory, household_factory, recipe_factory
    ):
        self.household = household_factory.create()
        db.session.add(self.household)
        db.session.commit()

        # Create library of recipes
        self.recipes = recipe_factory.create_batch(30, household=self.household)
        db.session.add_all(self.recipes)
        db.session.commit()

        # Create 7 day history of meals (1x day)
        for i in range(0, 7):
            meal = Meal.create(
                date=dt.date.today() - dt.timedelta(days=i),
                household_id=self.household.id,
            )
            # assign 2x recipes to each meal
            recipe1 = self.recipes[random.randint(0, len(self.recipes) - 1)]
            recipe2 = self.recipes[random.randint(0, len(self.recipes) - 1)]
            meal.recipes.append(recipe1)
            meal.recipes.append(recipe2)
            print(f"Meal {meal.id} has recipes: {meal.recipes}")
            meal.save()

        self.meal = meal_factory.create(household=self.household)
        db.session.add(self.meal)
        db.session.commit()

        recipe = MealPlannerDAO.suggest_recipe_for_meal(self.meal)
        print(f"Suggested recipe: {recipe.name}")

        assert recipe is not None
