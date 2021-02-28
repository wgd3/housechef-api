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


class Ingredient(PkModel, LookupByNameMixin, TimestampMixin):
    """Model for individual ingredients in a recipe

    Ingredients here simply have names and (optionally) other properties. Ingredients are
    associated with recipes via the recipe_ingredients table, and that table contains measurement information
    """

    __tablename__ = "ingredients"

    """Columns"""
    # id
    # time_created
    # time_updated
    name = Column(db.String, unique=True, nullable=False)
    spoonacular_id = Column(db.Integer, unique=True)

    """Relationships"""
    recipes = relationship("RecipeIngredient", back_populates="ingredient")

    def __repr__(self):
        return f"<Ingredient {self.name}>"
