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
    household = relationship("Household", back_populates="meals")
    household_id = reference_col("households", nullable=False)

    recipes = relationship("MealRecipe", back_populates="meal")

    def __repr__(self):
        return f"<Meal for house {self.household.name} on {self.date}>"
