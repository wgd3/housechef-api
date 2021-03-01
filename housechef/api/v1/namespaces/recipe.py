from flask import url_for
from flask_jwt_extended import get_current_user, jwt_required
from flask_restx import fields, Namespace, Resource, reqparse, inputs
from flask_sqlalchemy import Pagination
from sqlalchemy import or_

from housechef.api.v1.schemas import RecipeSchema
from housechef.database.models import Recipe
from ..models import links_envelope, meta_envelope, response_envelope, pagination_parser
from ..dao import SpoonacularDAO

ns = Namespace("Recipes", description="Recipe Operations")

response_env = ns.model(response_envelope.get("name"), response_envelope.get("fields"))
meta_env = ns.model(meta_envelope.get("name"), meta_envelope.get("fields"))
links_env = ns.model(links_envelope.get("name"), links_envelope.get("fields"))

get_recipe_model = ns.clone("get_recipe_model", response_env, {"data": fields.Raw})
get_recipe_list_model = ns.inherit(
    "get_recipe_list_model",
    response_env,
    {
        "data": fields.List(fields.Raw),
        "_links": fields.Nested(links_env),
        "_meta": fields.Nested(meta_env),
    },
)

import_model = ns.model("recipe_import_model", {"url": fields.Url})


@ns.route("/<int:recipe_id>", endpoint="get_recipe")
class RecipeResource(Resource):
    """Single Recipe resource"""

    @ns.marshal_with(response_env)
    def get(self, recipe_id: int):
        schema = RecipeSchema()
        recipe = Recipe.query.get_or_404(recipe_id)
        return {
            "message": f"Returning recipe {recipe.name}",
            "data": schema.dump(recipe),
        }

    def put(self, recipe_id: int):
        pass

    def delete(self, recipe_id: int):
        pass


@ns.route("", endpoint="list_recipes")
class RecipeListResource(Resource):
    """Multi-recipe resource"""

    list_param_parser = pagination_parser.copy()
    list_param_parser.add_argument(
        "directions",
        type=inputs.boolean,
        default=False,
        help="Include directions from each recipe",
    )
    list_param_parser.add_argument(
        "ingredients",
        type=inputs.boolean,
        default=False,
        help="Include ingredients from each recipe",
    )

    @jwt_required(optional=True)
    @ns.doc(security="apiKey", parser=list_param_parser)
    @ns.marshal_with(get_recipe_list_model)
    def get(self):

        args = self.list_param_parser.parse_args()
        skip_fields = []
        if args.get("directions", False) is False:
            skip_fields.append("directions")
        if args.get("ingredients", False) is False:
            skip_fields.append("ingredients")

        schema = RecipeSchema(many=True, exclude=set(skip_fields))
        user = get_current_user()

        if user is None:
            recipes: Pagination = Recipe.query.filter(
                Recipe.household_id == None
            ).paginate(per_page=args.get("per_page"), page=args.get("page"))
        else:
            recipes: Pagination = Recipe.query.filter(
                or_(
                    Recipe.household_id == None,
                    Recipe.household_id == user.household_id,
                )
            ).paginate(per_page=args.get("per_page"), page=args.get("page"))

        return {
            "_meta": {
                "per_page": recipes.per_page,
                "page": recipes.page,
                "total_pages": recipes.pages,
                "total_items": recipes.total,
            },
            "_links": {
                "self": url_for("api_v1.list_recipes", **args),
                "next": url_for(
                    "api_v1.list_recipes", **{**args, **{"page": recipes.next_num}}
                )
                if recipes.has_next
                else None,
                "prev": url_for(
                    "api_v1.list_recipes", **{**args, **{"page": recipes.prev_num}}
                )
                if recipes.has_prev
                else None,
            },
            "message": f"returning {recipes.total} recipes",
            "data": schema.dump(recipes.items, many=True),
        }, 200

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
