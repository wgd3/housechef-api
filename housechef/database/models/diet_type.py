from housechef.extensions import db
from ..mixins import Column, LookupByNameMixin, PkModel, relationship, TimestampMixin


class DietType(PkModel, TimestampMixin, LookupByNameMixin):
    """Simple table for identifying diet types"""

    __tablename__ = "diet_types"

    """Columns"""
    # id
    # time_created
    # time_updated
    name = Column(db.String, unique=True, nullable=False)

    """Relationships"""
    recipes = relationship("RecipeDietType", back_populates="diet_type")

    def __repr__(self):
        return f"<DietType {self.name}>"
