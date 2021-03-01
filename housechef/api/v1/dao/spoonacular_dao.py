from typing import List

from flask import current_app
from sqlalchemy import or_

from housechef.extensions import spoon
from housechef.database.models import (
    Recipe,
    Ingredient,
    RecipeIngredient,
    Cuisine,
    RecipeCuisine,
    DishType,
    RecipeDishType,
)
from housechef.tasks import get_recipe_ingredient_nutrition


class SpoonacularDAO(object):
    @staticmethod
    def import_recipe(url: str, household_id: int = None):
        current_app.logger.debug(f"Attempting to import recipe from {url}")
        recipe = None
        nutrition_ingredients = []
        resp = spoon.extract_recipe_from_website(url)
        if resp.ok:
            recipe_data = resp.json()

            # create the actual recipe first
            try:
                recipe = Recipe.create(
                    name=recipe_data["title"],
                    recipe_url=recipe_data["sourceUrl"],
                    image_url=recipe_data["image"],
                    author="",
                    servings=recipe_data["servings"],
                    cook_time=recipe_data["cookingMinutes"]
                    if "cookingMinutes" in recipe_data
                    else recipe_data["readyInMinutes"],
                    directions=recipe_data["instructions"],
                    household_id=household_id,
                )
                current_app.logger.debug(
                    f"Created new recipe '{recipe.name}', creating ingredients..."
                )

            except Exception as e:
                current_app.logger.error(str(e))
                # TODO return 4XX

            # try to set up ingredients
            try:
                ingredient_list = recipe_data["extendedIngredients"]
                for i in ingredient_list:
                    ingredient_name = i["name"]
                    current_app.logger.debug(
                        f"Looking to see if {ingredient_name} is already in the database"
                    )
                    ingredient = Ingredient.query.filter(
                        or_(
                            Ingredient.name == ingredient_name,
                            Ingredient.spoonacular_id == i["id"],
                        )
                    ).one_or_none()
                    if ingredient is None:
                        # No matching ingredient in the database, create one before associating with recipe
                        ingredient = Ingredient.create(
                            name=ingredient_name, spoonacular_id=i["id"]
                        )
                        current_app.logger.debug(
                            f"Ingredient not found, added {ingredient.name} to database with id of {ingredient.id}"
                        )
                    else:
                        current_app.logger.debug(
                            f"Found {ingredient.name} already in database!"
                        )

                    # ingredient is now defined, whether just created or already in the db
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                        original_string=i["originalString"],
                        amount=i["amount"],
                        unit=i["unit"],
                        us_amount=i["measures"]["us"]["amount"],
                        us_unit_short=i["measures"]["us"]["unitShort"],
                        us_unit_long=i["measures"]["us"]["unitLong"],
                        metric_amount=i["measures"]["metric"]["amount"],
                        metric_unit_short=i["measures"]["metric"]["unitShort"],
                        metric_unit_long=i["measures"]["metric"]["unitLong"],
                    )
                    recipe.ingredients.append(recipe_ingredient)

                    nutrition_ingredients.append(
                        dict(
                            ingredient_id=ingredient.id,
                            ingredient_string=i["originalString"],
                            spoonacular_id=i["id"],
                        )
                    )

                current_app.logger.debug(
                    f"All ingredients created/added to recipe, saving..."
                )
                recipe.save()

                # TODO finish implementing nutrition lookup
                get_recipe_ingredient_nutrition.delay(nutrition_ingredients, recipe.id)

            except Exception as e:
                current_app.logger.error(
                    f"Error occurred while creating/adding ingredients to recipe: {str(e)}"
                )

            # attempt to associate one or more cuisines
            try:
                current_app.logger.debug(f"Associating cuisines with new recipe...")
                cuisines: List[str] = recipe_data["cuisines"]
                if len(cuisines) > 0:
                    for c in cuisines:
                        existing_cuisine = Cuisine.query.filter(
                            Cuisine.name == c
                        ).one_or_none()
                        if existing_cuisine is None:
                            current_app.logger.debug(f"Creating new cuisine: {c}")
                            existing_cuisine = Cuisine.create(name=c)
                            current_app.logger.debug(f"Created!")
                        recipe_cuisine = RecipeCuisine(
                            recipe_id=recipe.id, cuisine_id=existing_cuisine.id
                        )
                        recipe.cuisines.append(recipe_cuisine)
                    current_app.logger.debug(
                        f"All {len(cuisines)} cuisines associated with recipe, saving.."
                    )
                    recipe.save()

            except Exception as e:
                current_app.logger.error(
                    f"Error occurred while associating cuisines: {str(e)}"
                )

            # attempt to associate dish types
            try:
                current_app.logger.debug(f"Associating dish types with recipe..")
                dish_types: List[str] = recipe_data["dishTypes"]
                if len(dish_types) > 0:
                    for dt in dish_types:
                        dish_type = DishType.query.filter(
                            DishType.name == dt
                        ).one_or_none()
                        if dish_type is None:
                            dish_type = DishType.create(name=dt)
                            current_app.logger.debug(
                                f"Created new dish type '{dish_type.name}' for recipe!"
                            )
                        recipe_dish_type = RecipeDishType(
                            recipe_id=recipe.id, dish_type_id=dish_type.id
                        )
                        recipe.dish_types.append(recipe_dish_type)
                    current_app.logger.debug(
                        f"Associated {len(dish_types)} dish types with recipe"
                    )
                    recipe.save()
            except Exception as e:
                current_app.logger.error(
                    f"Error occurred while associating dish types: {str(e)}"
                )

        else:
            current_app.logger.error(
                f"Error importing recipe from {url}: {resp.reason}"
            )
            # TODO return 4XX

        return recipe
