from housechef.extensions import db
from ..mixins import Column, LookupByNameMixin, PkModel, relationship, TimestampMixin


class Cuisine(PkModel, LookupByNameMixin, TimestampMixin):
    """Simple table for holding the various cuisine types"""

    __tablename__ = "cuisines"

    """Columns"""
    # id
    # time_created
    # time_updated
    name = Column(db.String(128), unique=True, nullable=False)

    """Relationships"""
    recipes = relationship("RecipeCuisine", back_populates="cuisine")

    def __repr__(self):
        return f"<Cuisine {self.name}>"
