from housechef.extensions import db
from ..mixins import Column, PkModel, reference_col, relationship, TimestampMixin


class Note(PkModel, TimestampMixin):
    __tablename__ = "notes"

    """Columns"""
    # id
    # time_created
    # time_updated
    text = Column(db.Text, nullable=False)

    """Relationships"""
    recipe = relationship("Recipe", back_populates="notes")
    recipe_id = reference_col("recipes", nullable=False)
