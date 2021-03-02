from http import HTTPStatus

from flask import current_app
from flask_jwt_extended import jwt_required
from flask_restx import fields, Namespace, Resource
from flask_sqlalchemy import Model

from ..models import links_envelope, meta_envelope, response_envelope


class RestfulNamespaceGenerator(object):
    _ns: Namespace = None
    _model: Model = None

    def create_restful_namespace(self, name: str, description: str) -> Namespace:
        current_app.logger.debug(f"Creating the {name} Namespace")

        # create and set up namespace
        ns = Namespace(name, description=description)

        response_env = ns.model(
            response_envelope.get("name"), response_envelope.get("fields")
        )
        meta_env = ns.model(meta_envelope.get("name"), meta_envelope.get("fields"))
        links_env = ns.model(links_envelope.get("name"), links_envelope.get("fields"))

        get_entity_model = ns.clone(
            f"get_entity_model", response_envelope, {"data": fields.Raw}
        )
        get_entity_list_model = ns.clone(
            f"get_entity_list_model",
            response_envelope,
            {
                "data": fields.List(fields.Raw),
                "_meta": fields.Nested(meta_env),
                "_links": fields.Nested(links_env),
            },
        )

        self._ns = ns
        return ns

    def create_entity_resource(
            self,
            ns: Namespace,
            obj_model,
            obj_schema,
            route: str,
            endpoint: str,
            requires_jwt: bool,
    ) -> Resource:

        gem = self._ns.models.get("get_entity_model")

        @ns.route(route, endpoint=endpoint)
        @ns.response(HTTPStatus.OK.value, HTTPStatus.OK.phrase)
        @ns.response(
            HTTPStatus.INTERNAL_SERVER_ERROR.value,
            HTTPStatus.INTERNAL_SERVER_ERROR.phrase,
        )
        @ns.response(HTTPStatus.NOT_FOUND.value, HTTPStatus.NOT_FOUND.phrase)
        @ns.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.phrase)
        class EntityResource(Resource):
            @jwt_required(optional=requires_jwt)
            @ns.marshal_with(gem)
            def get(self, entity_id: int):
                resp_msg: str = None
                resp_data = None
                ret_code = None

                try:
                    schema = obj_schema()
                    entity = obj_model.query.get_or_404(entity_id)
                    resp_msg = (
                        f"Found {entity.name if hasattr(entity, 'name') else 'entity'}"
                    )
                    resp_data = schema.dump(entity)
                    ret_code = HTTPStatus.OK

                except Exception as e:
                    current_app.logger.error(
                        f"Error while getting entity with ID '{entity_id}'"
                    )
                    resp_msg = f"Error while getting entity with ID '{entity_id}'"
                    resp_data = str(e)
                    ret_code = HTTPStatus.INTERNAL_SERVER_ERROR

                return {"data": resp_data, "message": resp_msg}, ret_code

        return EntityResource
