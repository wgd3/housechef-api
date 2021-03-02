from http import HTTPStatus

from flask_restx import fields, inputs, Namespace, Resource

from housechef.database.models import Ingredient
from ..models import links_envelope, meta_envelope, pagination_parser, response_envelope
from ..schemas import IngredientSchema
from ..utils import (
    generate_link_metadata,
    generate_query_metadata,
    set_search_filter,
    set_sort_order,
)

ns = Namespace("Ingredients", description="Ingredient Operations")

response_env = ns.model(response_envelope.get("name"), response_envelope.get("fields"))
meta_env = ns.model(meta_envelope.get("name"), meta_envelope.get("fields"))
links_env = ns.model(links_envelope.get("name"), links_envelope.get("fields"))

get_ingredient_model = ns.clone(
    "get_ingredient_model", response_env, {"data": fields.Raw}
)
get_ingredient_list_model = ns.inherit(
    "get_ingredient_list_model",
    response_env,
    {
        "data": fields.List(fields.Raw),
        "_meta": fields.Nested(meta_env),
        "_links": fields.Nested(links_env),
    },
)


@ns.route("", endpoint="list_ingredients")
@ns.response(HTTPStatus.OK.value, HTTPStatus.OK.phrase, model=get_ingredient_list_model)
@ns.response(HTTPStatus.BAD_REQUEST.value, HTTPStatus.BAD_REQUEST.phrase)
@ns.response(
    HTTPStatus.SERVICE_UNAVAILABLE.value, HTTPStatus.SERVICE_UNAVAILABLE.phrase
)
class IngredientListResource(Resource):
    """Ingredient List Resource"""

    param_parser = pagination_parser.copy()
    param_parser.add_argument(
        "filter",
        type=inputs.regex("^\w\w\w+$"),
        help="Search for a ingredient containing this text - must be at least 3 characters!",
        required=False,
        trim=True,
    )

    @ns.doc(parser=param_parser)
    def get(self):
        args = self.param_parser.parse_args()

        schema = IngredientSchema(many=True)
        ingredients = set_sort_order(Ingredient.query, Ingredient, **args)

        if args.get("filter") is not None:
            ingredients = set_search_filter(
                ingredients,
                Ingredient,
                search_field="name",
                search_value=args.get("filter"),
            ).all()
            return {
                       "_meta": {},
                       "_links": {},
                       "message": f"Found {len(ingredients)} ingredient{'' if len(ingredients) == 1 else 's'} matching '{args.get('filter')}'",
                       "data": schema.dump(ingredients, many=True),
                   }, 200

        ingredients = ingredients.paginate(args.get("page"), args.get("per_page"))

        return {
                   **generate_query_metadata(ingredients),
                   **generate_link_metadata(ingredients, "api_v1.list_ingredients", **args),
                   "message": f"Returning {ingredients.total} ingredients",
                   "data": schema.dump(ingredients.items, many=True),
               }, 200
