from typing import List

from flask import current_app

from sqlalchemy import and_
import time

from housechef.extensions import celery, spoon, db
from housechef.database.models import Recipe, Ingredient, RecipeIngredient


@celery.task(bind=True)
def get_recipe_ingredient_nutrition(
    self, recipe_ingredients: List[object], recipe_id: int
):
    recipe: Recipe = Recipe.get_by_id(recipe_id)
    ingredient_strings = [i["ingredient_string"] for i in recipe_ingredients]
    current_app.logger.debug(
        f"Using the following ingredients for lookup in recipe #{recipe_id}:\n{', '.join(ingredient_strings)}"
    )

    try:
        resp = spoon.parse_ingredients(
            "\n".join(ingredient_strings),
            servings=recipe.servings,
            includeNutrition=True,
        )
        resp_json = resp.json()
        # for each ingredient returned in the API response
        for ingredient_nutrition_obj in resp_json:
            # find the matching ingredient that was originally passed in
            recipe_ingredient_details = next(
                (
                    i
                    for i in recipe_ingredients
                    if i["spoonacular_id"] == ingredient_nutrition_obj["id"]
                ),
                None,
            )
            recipe_ingredient: RecipeIngredient = RecipeIngredient.query.filter(
                and_(
                    RecipeIngredient.recipe_id == recipe_id,
                    RecipeIngredient.ingredient_id
                    == recipe_ingredient_details["ingredient_id"],
                )
            ).one_or_none()
            if recipe_ingredient is not None:
                current_app.logger.debug(
                    f"Updating nutrients for {recipe_ingredient.ingredient.name}"
                )
                nutrients = ingredient_nutrition_obj["nutrition"]["nutrients"]
                recipe_ingredient.caffeine = next(
                    (n["amount"] for n in nutrients if n["name"] == "Caffeine"), None
                )
                recipe_ingredient.calcium = next(
                    (n["amount"] for n in nutrients if n["name"] == "Calcium"), None
                )
                recipe_ingredient.calories = next(
                    (n["amount"] for n in nutrients if n["name"] == "Calories"), None
                )
                recipe_ingredient.carbohydrates = next(
                    (n["amount"] for n in nutrients if n["name"] == "Carbohydrates"),
                    None,
                )
                recipe_ingredient.cholesterol = next(
                    (n["amount"] for n in nutrients if n["name"] == "Cholesterol"),
                    None,
                )
                recipe_ingredient.choline = next(
                    (n["amount"] for n in nutrients if n["name"] == "Choline"),
                    None,
                )
                recipe_ingredient.copper = next(
                    (n["amount"] for n in nutrients if n["name"] == "Copper"),
                    None,
                )
                recipe_ingredient.fat = next(
                    (n["amount"] for n in nutrients if n["name"] == "Fat"), None
                )
                recipe_ingredient.fiber = next(
                    (n["amount"] for n in nutrients if n["name"] == "Fiber"), None
                )
                recipe_ingredient.folate = next(
                    (n["amount"] for n in nutrients if n["name"] == "Folate"), None
                )
                recipe_ingredient.folic_acid = next(
                    (n["amount"] for n in nutrients if n["name"] == "Folic Acid"), None
                )
                recipe_ingredient.iron = next(
                    (n["amount"] for n in nutrients if n["name"] == "Iron"), None
                )
                recipe_ingredient.magnesium = next(
                    (n["amount"] for n in nutrients if n["name"] == "Magnesium"), None
                )
                recipe_ingredient.manganese = next(
                    (n["amount"] for n in nutrients if n["name"] == "Manganese"), None
                )
                recipe_ingredient.mono_unsaturated_fat = next(
                    (
                        n["amount"]
                        for n in nutrients
                        if n["name"] == "Mono Unsaturated Fat"
                    ),
                    None,
                )
                recipe_ingredient.net_carbohydrates = next(
                    (
                        n["amount"]
                        for n in nutrients
                        if n["name"] == "Net Carbohydrates"
                    ),
                    None,
                )
                recipe_ingredient.phosphorus = next(
                    (n["amount"] for n in nutrients if n["name"] == "Phosphorus"), None
                )
                recipe_ingredient.poly_unsaturated_fat = next(
                    (
                        n["amount"]
                        for n in nutrients
                        if n["name"] == "Poly Unsaturated Fat"
                    ),
                    None,
                )
                recipe_ingredient.potassium = next(
                    (n["amount"] for n in nutrients if n["name"] == "Potassium"), None
                )
                recipe_ingredient.protein = next(
                    (n["amount"] for n in nutrients if n["name"] == "Protein"), None
                )
                recipe_ingredient.saturated_fat = next(
                    (n["amount"] for n in nutrients if n["name"] == "Saturated Fat"),
                    None,
                )
                recipe_ingredient.selenium = next(
                    (n["amount"] for n in nutrients if n["name"] == "Selenium"), None
                )
                recipe_ingredient.sodium = next(
                    (n["amount"] for n in nutrients if n["name"] == "Sodium"), None
                )
                recipe_ingredient.sugar = next(
                    (n["amount"] for n in nutrients if n["name"] == "Sugar"), None
                )
                recipe_ingredient.vitamin_a = next(
                    (n["amount"] for n in nutrients if n["name"] == "Vitamin A"), None
                )
                recipe_ingredient.vitamin_b1 = next(
                    (n["amount"] for n in nutrients if n["name"] == "Vitamin B1"), None
                )
                recipe_ingredient.vitamin_b12 = next(
                    (n["amount"] for n in nutrients if n["name"] == "Vitamin B12"), None
                )
                recipe_ingredient.vitamin_b2 = next(
                    (n["amount"] for n in nutrients if n["name"] == "Vitamin B2"), None
                )
                recipe_ingredient.vitamin_b3 = next(
                    (n["amount"] for n in nutrients if n["name"] == "Vitamin B3"), None
                )
                recipe_ingredient.vitamin_b5 = next(
                    (n["amount"] for n in nutrients if n["name"] == "Vitamin B5"), None
                )
                recipe_ingredient.vitamin_b6 = next(
                    (n["amount"] for n in nutrients if n["name"] == "Vitamin B6"), None
                )
                recipe_ingredient.vitamin_c = next(
                    (n["amount"] for n in nutrients if n["name"] == "Vitamin C"), None
                )
                recipe_ingredient.vitamin_d = next(
                    (n["amount"] for n in nutrients if n["name"] == "Vitamin D"), None
                )
                recipe_ingredient.vitamin_e = next(
                    (n["amount"] for n in nutrients if n["name"] == "Vitamin E"), None
                )
                recipe_ingredient.vitamin_k = next(
                    (n["amount"] for n in nutrients if n["name"] == "Vitamin K"), None
                )
                recipe_ingredient.zinc = next(
                    (n["amount"] for n in nutrients if n["name"] == "Zinc"), None
                )

                db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error while parsing ingredients:\n{str(e)}")

    return "OK"
