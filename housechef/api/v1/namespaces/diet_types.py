from http import HTTPStatus

from flask_jwt_extended import jwt_required
from flask_restx import fields, Namespace, Resource

from housechef.database.models import DietType
from housechef.extensions import db
from ..models import links_envelope, meta_envelope, response_envelope, pagination_parser
from ..schemas import DietTypeSchema
from ..utils import role_required
from ..dao import SqlalchemyDAO

ns = Namespace("Diet Types", description="Diet Type Operations")

response_env = ns.model(response_envelope.get("name"), response_envelope.get("fields"))
meta_env = ns.model(meta_envelope.get("name"), meta_envelope.get("fields"))
links_env = ns.model(links_envelope.get("name"), links_envelope.get("fields"))

diet_type_model = ns.model(
    DietTypeSchema.get_restx_model().name, DietTypeSchema.get_restx_model()
)

get_diet_type_model = ns.clone(
    "get_diet_type_model", response_env, {"data": fields.Nested(diet_type_model)}
)
get_diet_type_list_model = ns.inherit(
    "get_diet_type_list_model",
    response_env,
    {
        "data": fields.List(fields.Nested(diet_type_model)),
        "_meta": fields.Nested(meta_env),
        "_links": fields.Nested(links_env),
    },
)


@ns.route("", endpoint="list_diet_types")
@ns.response(HTTPStatus.OK.value, HTTPStatus.OK.phrase)
@ns.response(
    HTTPStatus.INTERNAL_SERVER_ERROR.value, HTTPStatus.INTERNAL_SERVER_ERROR.phrase
)
class DietTypeListResource(Resource):

    list_parser = pagination_parser.copy()

    @ns.marshal_with(get_diet_type_list_model)
    @ns.expect(list_parser)
    def get(self):
        args = self.list_parser.parse_args()

        ret_json, ret_code = SqlalchemyDAO.get_entity_list(
            DietType, DietTypeSchema, "api_v1.list_diet_types", skip_fields=[], **args
        )
        return ret_json, ret_code

    @role_required("Admin")
    @ns.doc(security="apiKey")
    @ns.expect(diet_type_model)
    @ns.marshal_with(get_diet_type_model)
    @ns.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.phrase)
    @ns.response(HTTPStatus.BAD_REQUEST.value, HTTPStatus.BAD_REQUEST.phrase)
    @ns.response(HTTPStatus.CREATED.value, HTTPStatus.CREATED.phrase)
    def post(self):
        schema = DietTypeSchema()
        diet_type = schema.load(ns.payload)
        db.session.add(diet_type)
        db.session.commit()

        return {
            "data": schema.dump(diet_type),
            "message": f"Created new diet type '{diet_type.name}'",
        }, 201


@ns.route("/<int:diet_type_id>", endpoint="get_diet_type")
@ns.response(HTTPStatus.OK.value, HTTPStatus.OK.phrase)
@ns.response(
    HTTPStatus.INTERNAL_SERVER_ERROR.value, HTTPStatus.INTERNAL_SERVER_ERROR.phrase
)
class DietTypeListResource(Resource):
    @ns.marshal_with(get_diet_type_model)
    @ns.response(HTTPStatus.NOT_FOUND.value, HTTPStatus.NOT_FOUND.phrase)
    def get(self, diet_type_id: int):
        ret_json, ret_code = SqlalchemyDAO.get_entity_by_id(
            diet_type_id, DietType, DietTypeSchema
        )
        return ret_json, ret_code

    @role_required("Admin")
    @ns.expect(diet_type_model, validate=True)
    @ns.doc(security="apiKey")
    @ns.marshal_with(get_diet_type_model)
    @ns.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.phrase)
    @ns.response(HTTPStatus.BAD_REQUEST.value, HTTPStatus.BAD_REQUEST.phrase)
    def put(self, diet_type_id: int):
        schema = DietTypeSchema()
        diet_type = DietType.query.get_or_404(diet_type_id)
        diet_type.update(**ns.payload)
        return {
            "data": schema.dump(diet_type),
            "message": f"Updated diet type '{diet_type.name}!'",
        }, 200

    @role_required("Admin")
    @ns.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.phrase)
    @ns.doc(security="apiKey")
    def delete(self, diet_type_id: int):
        ret_json, ret_code = SqlalchemyDAO.delete_entity(diet_type_id, DietType)
        return ret_json, ret_code
