from flask_jwt_extended import jwt_required
from flask_restx import fields, Namespace, Resource

from housechef.database.models import Cuisine
from housechef.extensions import db
from ..models import links_envelope, meta_envelope, response_envelope
from ..schemas import CuisineSchema
from ..utils import role_required

ns = Namespace("Cuisines", description="Cuisine Operations")

response_env = ns.model(response_envelope.get("name"), response_envelope.get("fields"))
meta_env = ns.model(meta_envelope.get("name"), meta_envelope.get("fields"))
links_env = ns.model(links_envelope.get("name"), links_envelope.get("fields"))

cuisine_model = ns.model(
    CuisineSchema.get_restx_model().name, CuisineSchema.get_restx_model()
)

get_cuisine_model = ns.clone(
    "get_ingredient_model", response_env, {"data": fields.Nested(cuisine_model)}
)
get_cuisine_list_model = ns.inherit(
    "get_ingredient_list_model",
    response_env,
    {
        "data": fields.List(fields.Nested(cuisine_model)),
        "_meta": fields.Nested(meta_env),
        "_links": fields.Nested(links_env),
    },
)


@ns.route("", endpoint="list_cuisines")
class CuisineListResource(Resource):
    @ns.marshal_with(get_cuisine_list_model)
    def get(self):
        schema = CuisineSchema()
        query = Cuisine.query.all()
        return {
                   "data": schema.dump(query, many=True),
                   "message": f"Returning {len(query)} cuisines",
               }, 200

    @jwt_required()
    @ns.doc(security="apiKey")
    @ns.expect(cuisine_model)
    @ns.marshal_with(get_cuisine_model)
    def post(self):
        schema = CuisineSchema()
        cuisine = schema.load(ns.payload)
        db.session.add(cuisine)
        db.session.commit()

        return {
                   "data": schema.dump(cuisine),
                   "message": f"Created {cuisine.name}",
               }, 201


@ns.route("/<int:cuisine_id>", endpoint="get_cuisine")
class CuisineResource(Resource):
    @ns.marshal_with(get_cuisine_model)
    def get(self, cuisine_id: int):
        schema = CuisineSchema()
        cuisine = Cuisine.query.get_or_404(cuisine_id)
        return {
                   "data": schema.dump(cuisine),
                   "message": f"Returning cuisine '{cuisine.name}'",
               }, 200

    @jwt_required()
    @role_required("Admin")
    @ns.expect(cuisine_model, validate=True)
    @ns.marshal_with(get_cuisine_model)
    def put(self, cuisine_id):
        """Modify cuisine data - requires Admin role"""
        schema = CuisineSchema()
        cuisine = Cuisine.query.get_or_404(cuisine_id)
        cuisine.update(**ns.payload)
        return {
            "data": schema.dump(cuisine),
            "message": f"Updated cuisine '{cuisine.name}!'",
        }

    @jwt_required()
    @role_required("Admin")
    def delete(self, cuisine_id):
        """Delete cuisines - requires Admin role"""
        cuisine = Cuisine.query.get_or_404(cuisine_id)
        cuisine.delete()
        return {"data": None, "messge": "Deleted cuisine"}, 200
