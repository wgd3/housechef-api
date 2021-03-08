from flask import url_for
from flask_jwt_extended import get_current_user, jwt_required
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restx import fields, inputs, Namespace, Resource
from flask_sqlalchemy import Pagination
from sqlalchemy import or_

from housechef.extensions import db
from housechef.api.v1.schemas import RecipeSchema
from housechef.database.models import Recipe
from ..dao import SpoonacularDAO, SqlalchemyDAO, RecipeDAO
from ..models import links_envelope, meta_envelope, pagination_parser, response_envelope
from ..utils import (
    set_search_filter,
    set_sort_order,
    generate_query_metadata,
    generate_link_metadata,
)

ns = Namespace("Recipes", description="Recipe Operations")

response_env = ns.model(response_envelope.get("name"), response_envelope.get("fields"))
meta_env = ns.model(meta_envelope.get("name"), meta_envelope.get("fields"))
links_env = ns.model(links_envelope.get("name"), links_envelope.get("fields"))

recipe_model = ns.model(
    RecipeSchema.get_restx_model().name, RecipeSchema.get_restx_model()
)

get_recipe_model = ns.clone(
    "get_recipe_model", response_env, {"data": fields.Nested(recipe_model)}
)
get_recipe_list_model = ns.inherit(
    "get_recipe_list_model",
    response_env,
    {
        "data": fields.List(fields.Nested(recipe_model)),
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
        ret_json, ret_code = SqlalchemyDAO.get_entity_by_id(
            recipe_id, Recipe, RecipeSchema
        )
        return ret_json, ret_code

    @jwt_required()
    @ns.marshal_with(get_recipe_model)
    @ns.expect(recipe_model)
    @ns.doc(security="apiKey")
    def put(self, recipe_id: int):
        recipe = Recipe.query.get_or_404(recipe_id)
        user = get_current_user()
        if recipe.household_id is not None and user.household_id != recipe_id:
            raise NoAuthorizationError("User does not have access to this recipe!")
        # schema = RecipeSchema()
        # recipe = schema.load(ns.payload, instance=recipe)
        # db.session.commit()
        # return {"message": f"Recipe updated", "data": schema.dump(recipe)}, 200
        return RecipeDAO.update_recipe(recipe_id, ns.payload, append=False)

    @jwt_required()
    @ns.marshal_with(get_recipe_model)
    @ns.expect(recipe_model)
    @ns.doc(security="apiKey")
    def patch(self, recipe_id: int):
        recipe = Recipe.query.get_or_404(recipe_id)
        user = get_current_user()
        if recipe.household_id is not None and user.household_id != recipe_id:
            raise NoAuthorizationError("User does not have access to this recipe!")
        # schema = RecipeSchema()
        # recipe = schema.load(ns.payload, instance=recipe)
        # db.session.commit()
        # return {"message": f"Recipe updated", "data": schema.dump(recipe)}, 200
        return RecipeDAO.update_recipe(recipe_id, ns.payload, append=True)

    def delete(self, recipe_id: int):
        recipe = Recipe.query.get_or_404(recipe_id)
        user = get_current_user()
        if recipe.household_id is not None and user.household_id != recipe_id:
            raise NoAuthorizationError("User does not have access to this recipe!")
        ret_json, ret_code = SqlalchemyDAO.delete_entity(recipe_id, Recipe)
        return ret_json, ret_code


@ns.route("", endpoint="list_recipes")
class RecipeListResource(Resource):
    """Multi-recipe resource"""

    # _diet_types = []

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
    @ns.doc(security="apiKey")
    @ns.expect(list_param_parser)
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
            recipes = Recipe.query.filter(Recipe.household_id == None)
        else:
            recipes = Recipe.query.filter(
                or_(
                    Recipe.household_id == None,
                    Recipe.household_id == user.household_id,
                )
            )
        query = set_sort_order(recipes, Recipe, **args).paginate(
            per_page=args.get("per_page"), page=args.get("page")
        )

        return {
            **generate_query_metadata(query),
            **generate_link_metadata(query, "api_v1.list_recipes", **args),
            "message": f"returning {query.total} recipes",
            "data": schema.dump(query.items, many=True),
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
