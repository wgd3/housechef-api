from sqlalchemy.ext.hybrid import hybrid_property

from housechef.database.mixins import (
    LookupByNameMixin,
    PkModel,
    reference_col,
    relationship,
    TimestampMixin,
)
from housechef.extensions import db, jwt, pwd_context


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
    roles = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = pwd_context.hash(value)

    # Register a callback function that takes whatever object is passed in as the
    # identity when creating JWTs and converts it to a JSON serializable format.
    @staticmethod
    @jwt.user_identity_loader
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
    @jwt.user_lookup_loader
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
