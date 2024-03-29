from sqlalchemy.ext.associationproxy import association_proxy

from housechef.extensions import db
from ..mixins import Column, PkModel, reference_col, relationship, TimestampMixin


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

    meal_recipes = relationship(
        "MealRecipe", back_populates="meal", cascade="all, delete-orphan"
    )
    recipes = association_proxy(
        "meal_recipes",
        "recipe",
    )

    @property
    def nutrition(self):
        return {
            "calories": sum([r.recipe.calories for r in self.recipes]),
            "fat": sum([r.recipe.fat for r in self.recipes]),
            "protein": sum([r.recipe.protein for r in self.recipes]),
            "carbohydrates": sum([r.recipe.carbohydrates for r in self.recipes]),
            "fiber": sum([r.recipe.fiber for r in self.recipes]),
            "sodium": sum([r.recipe.sodium for r in self.recipes]),
            "net_carbohydrates": sum(
                [r.recipe.net_carbohydrates for r in self.recipes]
            ),
        }

    def __repr__(self):
        return f"<Meal for house {self.household.name} on {self.date}>"
