from http import HTTPStatus
from flask_jwt_extended import current_user, jwt_required


from flask_restx import Namespace, fields, Resource, inputs

from housechef.database.models import Household
from ..utils import (
    set_sort_order,
    set_search_filter,
    generate_query_metadata,
    generate_link_metadata,
)
from ..schemas import HouseholdSchema
from ..models import links_envelope, meta_envelope, response_envelope, pagination_parser

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
