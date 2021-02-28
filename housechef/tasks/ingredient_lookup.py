from typing import List

from flask import current_app

from sqlalchemy import and_
import time

from housechef.extensions import celery, spoon
from housechef.database.models import Recipe, Ingredient, RecipeIngredient


@celery.task(bind=True)
def get_recipe_ingredient_nutrition(
    self, recipe_ingredients_ids: List[int], recipe_id: int
):
    recipe: Recipe = Recipe.get_by_id(recipe_id)
    percent_complete = 0
    for idx, r_i_id in enumerate(recipe_ingredients_ids):
        recipe_ingredient = RecipeIngredient.query.filter(
            and_(
                RecipeIngredient.recipe_id == recipe_id,
                RecipeIngredient.ingredient_id == r_i_id,
            )
        ).one_or_none()
        if recipe_ingredient is not None:
            current_app.logger.debug(
                f"Looking up nutritional information for {recipe_ingredient.ingredient.name}"
            )
            # res = spoon.parse_ingredients(recipe_ingredient, recipe.servings)

        else:
            current_app.logger.error(
                f"Could not find ingredient with id {r_i_id} in recipe number {recipe_id}!"
            )

        percent_complete = ((idx + 1) / len(recipe_ingredients_ids)) * 100
        current_app.logger.debug(
            f"Recipe ingredient lookup task is {percent_complete}% complete"
        )
        self.update_state(
            state="PROGRESS",
            meta=dict(
                current=idx + 1,
                total=len(recipe_ingredients_ids),
                status=f"{percent_complete}% Complete",
            ),
        )
        time.sleep(1)

    return "OK"
