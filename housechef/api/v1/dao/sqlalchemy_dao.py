from http import HTTPStatus
from typing import List

from flask import current_app, abort
from flask_marshmallow import Schema
from flask_sqlalchemy import Model

from sqlalchemy import or_, func, and_, not_, exc

from marshmallow.exceptions import MarshmallowError

from housechef.exceptions import (
    EntityNotFoundError,
    HousechefDatabaseOpsError,
    HousechefSerializationError,
)

from ..utils import set_sort_order, generate_link_metadata, generate_query_metadata


class SqlalchemyDAO(object):
    @staticmethod
    def get_entity_by_id(
        entity_id: int,
        model: Model,
        model_schema: Schema,
    ):
        """
        Generic method for GET requests to simplify error handling and database ops

        TODO: implement a way to pass validator method for unauthorized reqs

        Args:
            entity_id:
            model:
            model_schema:

        Returns:

        """
        schema = model_schema()

        try:
            entity = model.query.filter(model.id == entity_id).one_or_none()
        except exc.SQLAlchemyError as sqle:
            current_app.logger.error(
                f"Error occurred while retrieving entity by ID '{str(sqle)}'"
            )
            current_app.logger.debug(f"Error details:\n{sqle.args}")
            raise HousechefDatabaseOpsError(
                message=f"Unknown database error occurred", data=None
            )

        if entity is None:
            raise EntityNotFoundError(
                message=f"Could not find entity with ID {entity_id}"
            )

        try:
            ret_data = schema.dump(entity)
        except MarshmallowError as me:
            current_app.logger.error(
                f"Unknown Marshmallow error occurred while deserializing data:\n{str(me)}"
            )
            raise HousechefSerializationError(
                message="An error occurred while serializing data for this object"
            )

        return {
            "data": ret_data,
            "message": f"Returning {model.__class__} with ID {entity_id}",
        }, HTTPStatus.OK

    @staticmethod
    def delete_entity(entity_id: int, model: Model):

        try:
            entity = model.query.filter(model.id == entity_id).one_or_none()
        except exc.SQLAlchemyError as sqle:
            current_app.logger.error(
                f"Error occurred while retrieving entity by ID '{str(sqle)}'"
            )
            current_app.logger.debug(f"Error details:\n{sqle.args}")
            raise HousechefDatabaseOpsError(
                message=f"Unknown database error occurred", data=None
            )

        if entity is None:
            raise EntityNotFoundError(
                message=f"Could not find entity with ID {entity_id}"
            )

        try:
            entity.delete()
        except exc.SQLAlchemyError as sqle:
            current_app.logger.error(
                f"Error occurred while deleting entity with ID {entity_id}: '{str(sqle)}'"
            )
            current_app.logger.debug(f"Error details:\n{sqle.args}")
            raise HousechefDatabaseOpsError(
                message=f"A database error occurred while attempting to delete this entity",
                data=None,
            )

        return {"data": None, "message": "Successfully deleted object!"}, HTTPStatus.OK

    @staticmethod
    def get_entity_list(
        model,
        model_schema,
        endpoint: str,
        skip_fields: List = [],
        page: int = 1,
        per_page: int = 10,
        **kwargs,
    ):
        schema = model_schema(many=True, exclude=set(skip_fields))

        try:
            entities = set_sort_order(model.query, model, **kwargs).paginate(
                per_page=per_page, page=page
            )
        except exc.SQLAlchemyError as sqle:
            current_app.logger.error(f"Error occurred while retrieving entity list")
            current_app.logger.debug(f"Error details:\n{sqle.args}")
            raise HousechefDatabaseOpsError(
                message=f"Unknown database error occurred", data=None
            )

        try:
            ret_data = schema.dump(entities.items, many=True)
        except MarshmallowError as me:
            current_app.logger.error(
                f"Unknown Marshmallow error occurred while deserializing data:\n{str(me)}"
            )
            raise HousechefSerializationError(
                message="An error occurred while serializing data"
            )

        return {
            **generate_query_metadata(entities),
            **generate_link_metadata(entities, endpoint, **kwargs),
            "data": ret_data,
            "message": f"Returning {len(ret_data)} objects",
        }, 200
