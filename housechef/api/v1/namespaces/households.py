from http import HTTPStatus
import datetime as dt
from flask import current_app
from flask_jwt_extended import current_user, get_current_user, jwt_required


from flask_restx import Namespace, fields, Resource, inputs, reqparse

from housechef.extensions import db
from housechef.database.models import Household, Meal, Recipe, MealRecipe
from ..dao import HouseholdDAO
from ..utils import (
    set_sort_order,
    set_search_filter,
    generate_query_metadata,
    generate_link_metadata,
)
from ..schemas import HouseholdSchema, MealSchema
from ..models import (
    links_envelope,
    meta_envelope,
    response_envelope,
    pagination_parser,
    meal_model,
)

ns = Namespace("Households", description="Household Operations")

response_env = ns.model(response_envelope.get("name"), response_envelope.get("fields"))
meta_env = ns.model(meta_envelope.get("name"), meta_envelope.get("fields"))
links_env = ns.model(links_envelope.get("name"), links_envelope.get("fields"))

get_household_model = ns.clone(
    "get_household_model", response_env, {"data": fields.Raw}
)
get_household_list_model = ns.inherit(
    "get_household_list_model",
    response_env,
    {
        "data": fields.List(fields.Raw),
        "_meta": fields.Nested(meta_env),
        "_links": fields.Nested(links_env),
    },
)

ns.models[meal_model.name] = meal_model


@ns.route("", endpoint="list_households")
@ns.response(HTTPStatus.OK.value, HTTPStatus.OK.phrase, model=get_household_list_model)
@ns.response(HTTPStatus.BAD_REQUEST.value, HTTPStatus.BAD_REQUEST.phrase)
@ns.response(
    HTTPStatus.SERVICE_UNAVAILABLE.value, HTTPStatus.SERVICE_UNAVAILABLE.phrase
)
class HouseholdList(Resource):

    parser = pagination_parser.copy()

    def get(self):
        args = self.parser.parse_args()
        schema = HouseholdSchema(many=True)
        query = set_sort_order(Household.query, Household, **args).paginate(
            args.get("page"), args.get("per_page")
        )

        return {
            **generate_query_metadata(query),
            **generate_link_metadata(query, "api_v1.list_households", **args),
            "message": f"Returning {query.total} households",
            "data": schema.dump(query.items, many=True),
        }, 200


@ns.route("/meals", endpoint="household_meals")
@ns.response(HTTPStatus.OK.value, HTTPStatus.OK.phrase)
@ns.response(HTTPStatus.NOT_FOUND.value, HTTPStatus.NOT_FOUND.phrase)
@ns.response(
    HTTPStatus.SERVICE_UNAVAILABLE.value, HTTPStatus.SERVICE_UNAVAILABLE.phrase
)
class HouseholdMealListResource(Resource):

    date_parser = reqparse.RequestParser()
    date_parser.add_argument(
        "date", type=inputs.date, help="Specific day to search for"
    )

    @jwt_required()
    @ns.doc(security="apiKey", parser=date_parser)
    def get(self):
        args = self.date_parser.parse_args()
        schema = MealSchema(many=True)
        user = get_current_user()
        date = args.get("date") if args.get("date") is not None else dt.date.today()
        meals = HouseholdDAO.get_meals_for_day(user.household_id, date)
        return {
            "message": f"Found {len(meals)} meals planned for {date}",
            "data": schema.dump(meals, many=True),
        }, 200

    @jwt_required()
    @ns.doc(security="apiKey")
    # @ns.expect(meal_model, validate=True)
    @ns.response(
        HTTPStatus.CREATED.value, HTTPStatus.CREATED.phrase, model=response_env
    )
    def post(self):

        try:
            schema = MealSchema()
            meal = Meal.create(
                date=ns.payload["date"], household_id=ns.payload["household_id"]
            )
            current_app.logger.debug(f"Created meal with ID #{meal.id} for {meal.date}")
            if "recipes" in ns.payload and len(ns.payload["recipes"]) > 0:
                for recipe_id in ns.payload["recipes"]:
                    recipe = Recipe.get_by_id(recipe_id)
                    meal_recipe = MealRecipe(recipe_id=recipe.id, meal_id=meal.id)
                    meal.recipes.append(meal_recipe)
                    current_app.logger.debug(f"added {recipe.name} to meal #{meal.id}")
                meal.save()

        except Exception as e:
            current_app.logger.error(f"Error while creating meal: {str(e)}")
            return {"message": f"Could not create meal. {str(e)}", "data": None}, 400

        return {
            "message": f"Created meal for {meal.date}",
            "data": schema.dump(meal),
        }, 201
