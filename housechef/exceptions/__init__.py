from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow.exceptions import ValidationError, MarshmallowError


class HousechefException(Exception):
    def __init__(self, *args, **kwargs):
        self._message = kwargs.get("message")
        self._data = kwargs.get("data")

    @property
    def message(self):
        return self._message

    @property
    def data(self):
        return self._data


class EntityNotFoundError(HousechefException):
    """Database record not found"""


class EntityValidationError(HousechefException):
    """Incoming data for entity update is not valid"""


class EntityAlreadyExistsError(IntegrityError):
    """POST request is invalid due to a conflicting unique property"""


class HousechefDatabaseOpsError(HousechefException):
    """Generic SQLAlchemy error wrapper"""


class HousechefSerializationError(HousechefException):
    pass
