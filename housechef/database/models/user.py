from datetime import date, timedelta
from time import time
from jwt import encode as encode_jwt, decode as decode_jwt, InvalidTokenError

from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from sqlalchemy import event, inspect
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from housechef.database.mixins import (
    LookupByNameMixin,
    PkModel,
    reference_col,
    relationship,
    TimestampMixin,
)
from housechef.extensions import db, jwt as jwt_ext, pwd_context
from .role import Role


class User(PkModel, TimestampMixin, LookupByNameMixin):
    """Basic user model"""

    __tablename__ = "users"

    """Columns"""
    # id
    # time_created
    # time_updated
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    _password = db.Column("password", db.String, nullable=False)
    active = db.Column(db.Boolean, default=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    birthday = db.Column(db.Date)
    height_inches = db.Column(db.Float)
    weight_lbs = db.Column(db.Float)
    gender = db.Column(db.Enum("male", "female", name="gender_enum"))

    """Relationships"""
    tags = relationship("Tag", back_populates="user")
    household = relationship("Household", back_populates="users")
    household_id = reference_col("households")

    user_roles = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )
    roles = association_proxy("user_roles", "role")

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = pwd_context.hash(value)

    # Register a callback function that takes whatever object is passed in as the
    # identity when creating JWTs and converts it to a JSON serializable format.
    @staticmethod
    @jwt_ext.user_identity_loader
    def user_identity_lookup(user):
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "household_id": user.household_id,
        }

    # Register a callback function that loads a user from your database whenever
    # a protected route is accessed. This should return any python object on a
    # successful lookup, or None if the lookup failed for any reason (for example
    # if the user has been deleted from the database).
    @staticmethod
    @jwt_ext.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity["id"]).one_or_none()

    def has_role(self, role):
        return role in self.roles

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        if len(self.roles) == 0:
            # TODO add default roles!
            pass

    def __repr__(self):
        return "<User %s>" % self.username

    def get_access_token(self):
        jwt = create_access_token(
            identity=self, additional_claims=self.additional_claims
        )
        return jwt

    def get_refresh_token(self):
        jwt = create_refresh_token(
            identity=self, additional_claims=self.additional_claims
        )
        return jwt

    @property
    def additional_claims(self):
        return {"roles": [r.name for r in self.roles]}

    @property
    def age(self) -> int:
        if self.birthday is None:
            return None
        today = date.today()
        age = (
            today.year
            - self.birthday.year
            - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        )
        return age

    def get_password_reset_token(self, expires_in: int = 3600):
        return encode_jwt(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm=current_app.config["JWT_ALGORITHM"],
        )

    @classmethod
    def verify_password_reset_token(cls, token):
        user = None
        try:
            token_data = decode_jwt(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=[current_app.config["JWT_ALGORITHM"]],
            )
            user_id = token_data["reset_password"]
            user = cls.get_by_id(user_id)
        except InvalidTokenError as ite:
            current_app.logger.error(
                f"Someone is trying to use an invalid token to reset a user password!\n{str(ite)}"
            )

        return user


@event.listens_for(User, "after_insert")
def receive_after_insert(mapper, connection, target):
    @event.listens_for(db.session, "after_flush", once=True)
    def receive_after_flush(session, context):
        current_app.logger.debug(f"New user created, associating all default roles")
        roles = Role.query.filter(Role.default == True).all()
        insp = inspect(target)
        commit = False if insp.pending else True
        for r in roles:
            target.roles.append(r)
        target.save(commit=commit)
