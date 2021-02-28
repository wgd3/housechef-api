from housechef.extensions import db
from ..mixins import Column, PkModel, TimestampMixin, reference_col, relationship


class Meal(PkModel, TimestampMixin):

    __tablename__ = "meals"

    """Columns"""
    # id
    # time_created
    # time_updated
    date = Column(db.Date, nullable=False)

    """Relationships"""
    user = relationship("User", back_populates="meals")
    user_id = reference_col("users", nullable=False)

    recipes = relationship("MealRecipe", back_populates="meal")
