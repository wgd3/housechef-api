from housechef.extensions import db
from ..mixins import Column, LookupByNameMixin, PkModel, TimestampMixin, relationship


class DishType(PkModel, TimestampMixin, LookupByNameMixin):
    """Simple table for identifying recipe types"""

    __tablename__ = "dish_types"

    """Columns"""
    # id
    # time_created
    # time_updated
    name = Column(db.String, unique=True, nullable=False)

    """Relationships"""
    recipes = relationship("RecipeDishType", back_populates="dish_type")

    def __repr__(self):
        return f"<DishType {self.name}>"
