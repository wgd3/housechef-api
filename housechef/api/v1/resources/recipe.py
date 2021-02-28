from flask import request
from flask_restx import Resource

from housechef.extensions import db
from housechef.database.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    DishType,
    RecipeTag,
    Cuisine,
    Note,
    Tag,
    Meal,
    MealRecipe,
)
from ..schemas import RecipeSchema


class RecipeResource(Resource):
    """Single Recipe resource"""

    def get(self, recipe_id: int):
        schema = RecipeSchema()
        recipe = Recipe.query.get_or_404(recipe_id)
        return {"recipe": schema.dump(recipe)}

    def put(self, recipe_id: int):
        pass

    def delete(self, recipe_id: int):
        pass


class RecipeListResource(Resource):
    """Multi-recipe resource"""

    def get(self):
        pass

    def post(self):
        pass
