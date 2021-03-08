import datetime as dt
from http import HTTPStatus

from flask import current_app
from flask_jwt_extended import get_current_user, jwt_required
from flask_restx import fields, inputs, Namespace, reqparse, Resource
from marshmallow.utils import from_iso_date

from housechef.database.models import Household, Meal, Recipe
from ..dao import HouseholdDAO, SqlalchemyDAO
from ..models import (
    links_envelope,
    meal_model,
    meta_envelope,
    pagination_parser,
    response_envelope,
)
from ..schemas import HouseholdSchema, MealSchema
from ..utils import (
    generate_link_metadata,
    generate_query_metadata,
    role_required,
    set_sort_order,
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

    @jwt_required()
    @role_required("Admin")
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


@ns.route("<int:household_id>", endpoint="get_household")
@ns.response(HTTPStatus.OK.value, HTTPStatus.OK.phrase)
@ns.response(HTTPStatus.FORBIDDEN.value, HTTPStatus.FORBIDDEN.phrase)
@ns.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.phrase)
@ns.response(
    HTTPStatus.SERVICE_UNAVAILABLE.value, HTTPStatus.SERVICE_UNAVAILABLE.phrase
)
class HouseholdResource(Resource):
    @jwt_required()
    @ns.doc(security="apiKey")
    def get(self, household_id: int):
        user = get_current_user()

        if household_id != user.household_id:
            return {
                "message": "Requested household does not belong to the current user",
                "data": None,
            }, 403

        ret_json, ret_code = SqlalchemyDAO.get_entity_by_id(
            household_id, Household, HouseholdSchema
        )
        return ret_json, ret_code


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
    @ns.doc(security="apiKey")
    @ns.expect(date_parser)
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
        user = get_current_user()

        try:
            schema = MealSchema()

            # make sure these match!
            if user.household_id != ns.payload["household_id"]:
                raise IndexError("User household does not match meal payload!")

            meal = Meal.create(
                date=from_iso_date(ns.payload["date"]),
                household_id=ns.payload["household_id"],
                recipes=[],
            )
            current_app.logger.debug(f"Created meal with ID #{meal.id} for {meal.date}")
            if "recipes" in ns.payload and len(ns.payload["recipes"]) > 0:
                for recipe_id in ns.payload["recipes"]:
                    recipe = Recipe.get_by_id(recipe_id)
                    meal.recipes.append(recipe)
                    current_app.logger.debug(f"added {recipe.name} to meal #{meal.id}")
                meal.save()

        except ValueError as ve:
            current_app.logger.debug(f"Date format prevented meal from being created")
            return {"message": str(ve), "data": None}, 400
        except Exception as e:
            current_app.logger.error(f"Error while creating meal: {str(e)}")
            return {"message": f"Could not create meal. {str(e)}", "data": None}, 400

        return {
            "message": f"Created meal for {meal.date}",
            "data": schema.dump(meal),
        }, 201
