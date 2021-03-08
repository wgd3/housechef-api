import logging
from typing import List

from celery import states
from celery.utils.log import get_task_logger
from sqlalchemy import and_

from housechef.database.models import Recipe, RecipeIngredient
from housechef.extensions import celery, db, spoon

logger = get_task_logger(__name__)
logger.setLevel(logging.DEBUG)


@celery.task(bind=True)
def get_recipe_ingredient_nutrition(
    self, recipe_ingredients: List[object], recipe_id: int
):
    recipe: Recipe = Recipe.get_by_id(recipe_id)
    ingredient_strings = [i["ingredient_string"] for i in recipe_ingredients]
    logger.debug(
        f"Using the following ingredients for lookup in recipe #{recipe.id} - {recipe.name}:\n{', '.join(ingredient_strings)}"
    )
    self.update_state(state=states.STARTED)

    try:
        resp = spoon.parse_ingredients(
            "\n".join(ingredient_strings),
            servings=recipe.servings,
            includeNutrition=True,
        )
        resp_json = resp.json()
        # logger.debug("Grabbed response from Spoonacular, evaluating...")
        # for each ingredient returned in the API response
        for ingredient_idx, ingredient_nutrition_obj in enumerate(resp_json):
            # if the id is missing, the ingredient couldn't be found by spoonacular
            if "id" not in ingredient_nutrition_obj:
                logger.error(
                    f"Ingredient {ingredient_nutrition_obj['original']} does not have a Spoonacular ID, skipping..."
                )
                continue
            # find the matching ingredient that was originally passed in
            recipe_ingredient_details = next(
                (
                    i
                    for i in recipe_ingredients
                    if i["ingredient_string"] == ingredient_nutrition_obj["original"]
                ),
                None,
            )
            # TODO better way to handle duplicates below?
            recipe_ingredient: RecipeIngredient = RecipeIngredient.query.filter(
                and_(
                    RecipeIngredient.recipe_id == recipe_id,
                    RecipeIngredient.ingredient_id
                    == recipe_ingredient_details["ingredient_id"],
                )
            ).first()
            if recipe_ingredient is not None:
                # logger.debug(
                #     f"Updating nutrients for {recipe_ingredient.ingredient.name}"
                # )
                nutrients = ingredient_nutrition_obj["nutrition"]["nutrients"]
                find_and_populate_nutrients(nutrients, recipe_ingredient)

                # logger.debug(
                #     f"{recipe_ingredient.ingredient.name} has had all nutrients updated!"
                # )
                db.session.add(recipe_ingredient)
                db.session.commit()

                self.update_state(
                    state="PROGRESS",
                    meta={"total": len(resp.json()), "current": ingredient_idx},
                )

        # logger.debug(f"Recipe {recipe.name} macros have been updated:\n{recipe.macros}")

    except KeyError as ke:
        logger.error(f"Error looking up key '{str(ke)}'")
        self.update_state(state=states.FAILURE)

    except Exception as e:
        logger.error(f"Error while parsing ingredients:\n{str(e)}")
        self.update_state(state=states.FAILURE)

    return "OK"


def find_and_populate_nutrients(nutrient_list: List, ingredient_obj):
    for nutrient in nutrient_list:
        name = nutrient["name"]
        obj_attr = name.lower().replace(" ", "_")
        if hasattr(ingredient_obj, obj_attr):
            setattr(ingredient_obj, obj_attr, nutrient["amount"])
