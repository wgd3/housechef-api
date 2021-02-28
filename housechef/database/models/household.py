from sqlalchemy.ext.hybrid import hybrid_property

from housechef.extensions import db
from ..mixins import (
    Column,
    LookupByNameMixin,
    PkModel,
    TimestampMixin,
    reference_col,
    relationship,
)


class Household(PkModel, TimestampMixin):
    """Model for households, which are simple groupings of users"""

    __tablename__ = "households"

    """Columns"""
    name = Column(db.String(128), nullable=False, unique=True)

    """Relationships"""
    users = relationship("User", back_populates="household")
    recipes = relationship(
        "Recipe", back_populates="household", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return "<Household %s>" % self.name
