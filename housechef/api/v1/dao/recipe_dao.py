from flask import current_app

from housechef.database.models import (
    Cuisine,
    DishType,
    Recipe,
    RecipeDietType,
    RecipeIngredient,
    RecipeDishType,
    RecipeCuisine,
    RecipeTag,
    DietType,
)
from housechef.extensions import db
from housechef.exceptions import EntityValidationError

from ..schemas import RecipeSchema


class RecipeDAO(object):
    @staticmethod
    def update_recipe(recipe_id: int, data, append: bool = True):
        recipe = Recipe.query.get_or_404(recipe_id)

        diets = data.pop("diets", [])
        if len(diets) > 0:
            current_app.logger.debug(
                f"\nUpdating diet types associated with '{recipe.name}'"
            )
            for diet in diets:
                if not isinstance(diet, str):
                    raise EntityValidationError(
                        message=f"Diets list in payload must be a list of strings!",
                        data={"diets": diets},
                    )
                diet_to_assoc = DietType.query.filter(
                    DietType.name == diet.lower()
                ).one_or_none()
                if diet_to_assoc is None:
                    diet_to_assoc = DietType.create(name=diet.lower())
                    current_app.logger.debug(
                        f"Created new diet type '{diet_to_assoc.name}'"
                    )
                elif diet_to_assoc in recipe.diets and append:
                    current_app.logger.debug(
                        f"Diet type '{diet_to_assoc.name}' is already associated with recipe, skipping"
                    )
                    continue
                elif diet_to_assoc in recipe.diets and append is False:
                    current_app.logger.debug(
                        f"Diet type '{diet_to_assoc.name}' is associated with recipe, but we are replacing instead of appending. Removing this diet type!"
                    )
                    recipe.diets.remove(diet_to_assoc)
                    continue
                recipe.diets.append(diet_to_assoc)
                current_app.logger.debug(
                    f"Associated diet type '{diet_to_assoc.name}' with recipe!"
                )

        cuisines = data.pop("cuisines", [])
        if len(cuisines) > 0:
            current_app.logger.debug(
                f"\nUpdating cuisines associated with '{recipe.name}'"
            )
            if append is False:
                recipe.cuisines.clear()
            for cuisine in cuisines:
                if not isinstance(cuisine, str):
                    raise EntityValidationError(
                        message=f"Cuisine list in payload must be a list of strings!",
                        data={"cuisines": cuisines},
                    )
                cuisine_to_assoc = Cuisine.query.filter(
                    Cuisine.name == cuisine.lower()
                ).one_or_none()
                if cuisine_to_assoc is None:
                    cuisine_to_assoc = Cuisine.create(name=cuisine.lower())
                elif cuisine_to_assoc in recipe.cuisines:
                    current_app.logger.debug(
                        f"Cuisine '{cuisine_to_assoc.name}' is already associated with recipe, skipping"
                    )
                    continue
                # elif cuisine_to_assoc in recipe.cuisines and append is False:
                #     current_app.logger.debug(
                #         f"Cuisine '{cuisine_to_assoc.name}' is associated with recipe, but we are replacing instead of appending. Removing this cuisine!"
                #     )
                #     recipe.cuisines.remove(cuisine_to_assoc)
                #     continue
                recipe.cuisines.append(cuisine_to_assoc)
                current_app.logger.debug(f"Associated cuisine '{cuisine}' with recipe!")

        dish_types = data.pop("dish_types", [])
        if len(dish_types) > 0:
            current_app.logger.debug(
                f"\nUpdating dish_types associated with '{recipe.name}'"
            )
            for dish_type in dish_types:
                if not isinstance(dish_type, str):
                    raise EntityValidationError(
                        message=f"Dish type list in payload must be a list of strings!",
                        data={"dish_types": dish_types},
                    )
                dish_type_to_assoc = DishType.query.filter(
                    DishType.name == dish_type.lower()
                ).one_or_none()
                if dish_type_to_assoc is None:
                    dish_type_to_assoc = DishType.create(name=dish_type.lower())
                elif dish_type_to_assoc in recipe.dish_types:
                    current_app.logger.debug(
                        f"Dish type '{dish_type_to_assoc.name}' is already associated with recipe, skipping"
                    )
                    continue
                elif dish_type_to_assoc in recipe.dish_types and append is False:
                    current_app.logger.debug(
                        f"Dish type '{dish_type_to_assoc.name}' is associated with recipe, but we are replacing instead of appending. Removing this dish type!"
                    )
                    recipe.dish_types.remove(dish_type_to_assoc)
                    continue
                recipe.dish_types.append(dish_type_to_assoc)
                current_app.logger.debug(
                    f"Associated dish_type '{dish_type}' with recipe!"
                )

        # all necessary relationships have been popped from the data dict, so we're safe to update the
        # regular k/v pairs using update()
        recipe.update(**data)
        current_app.logger.debug(f"Recipe updated successfully!")
        schema = RecipeSchema()
        return {
            "data": schema.dump(recipe),
            "message": f"Recipe '{recipe.name}' updated successfully!",
        }, 200
