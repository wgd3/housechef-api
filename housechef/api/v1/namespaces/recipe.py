from flask_jwt_extended import get_current_user, jwt_required
from flask_restx import fields, Namespace, Resource
from sqlalchemy import or_

from housechef.api.v1.schemas import RecipeSchema
from housechef.database.models import Recipe
from ..dao import SpoonacularDAO

ns = Namespace("Recipes", description="Recipe Operations")

import_model = ns.model("recipe_import_model", {"url": fields.Url})


@ns.route("/<int:recipe_id>", endpoint="get_recipe")
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


@ns.route("", endpoint="list_recipes")
class RecipeListResource(Resource):
    """Multi-recipe resource"""

    @jwt_required(optional=True)
    @ns.doc(security="apiKey")
    def get(self):
        schema = RecipeSchema(many=True)
        user = get_current_user()
        if user is None:
            recipes = Recipe.query.filter(Recipe.household_id == None).all()
        else:
            recipes = Recipe.query.filter(
                or_(
                    Recipe.household_id == None,
                    Recipe.household_id == user.household_id,
                )
            ).all()

        return {"recipes": schema.dump(recipes)}, 200

    def post(self):
        pass


@ns.route("/import", endpoint="import_recipe")
class RecipeImportResource(Resource):
    """Route for analyzing a recipe using the Spoonacular API"""

    @ns.expect(import_model)
    @ns.doc(security="apiKey")
    @jwt_required(optional=True)
    def post(self):
        url = ns.payload["url"]
        user = get_current_user()
        recipe = SpoonacularDAO.import_recipe(
            url, user.household_id if user is not None else None
        )
        if recipe:
            schema = RecipeSchema()
            return {"recipe": schema.dump(recipe)}, 200
        else:
            return {}, 400
