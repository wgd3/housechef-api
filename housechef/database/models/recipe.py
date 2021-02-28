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


class Recipe(PkModel, TimestampMixin, LookupByNameMixin):
    """
    Model for recipe data.
    """

    __tablename__ = "recipes"

    """Columns"""
    # id
    # time_created
    # time_updated
    name = Column(db.String(128), nullable=False, unique=True)
    recipe_url = Column(db.String)
    image_url = Column(db.String)
    thumbnail_url = Column(db.String)
    author = Column(db.String)
    rating = Column(db.Integer)
    servings = Column(db.Integer, default=1)
    prep_time = Column(db.Integer)
    cook_time = Column(db.Integer)
    source_name = Column(db.String)
    _directions = Column(db.Text)

    """One (recipe) to One Relationships"""
    household_id = reference_col("households", nullable=True)
    household = relationship("Household", back_populates="recipes")

    """One (recipe) to Many Relationships"""
    cuisines = relationship(
        "RecipeCuisine", back_populates="recipe", cascade="all, delete-orphan"
    )
    dish_types = relationship(
        "RecipeDishType", back_populates="recipe", cascade="all, delete-orphan"
    )
    notes = relationship("Note", back_populates="recipe", cascade="all, delete-orphan")
    ingredients = relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan"
    )
    tags = relationship(
        "RecipeTag", back_populates="recipe", cascade="all, delete-orphan"
    )
    meals = relationship(
        "MealRecipe", back_populates="recipe", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Recipe #{self.id} - {self.name}>"

    @property
    def slug(self) -> str:
        return self.name.lower().replace(" ", "-")

    @property
    def directions(self):
        if self._directions is not None:
            return [step for step in self._directions.split("\n") if step.strip() != ""]
        return []

    @directions.setter
    def directions(self, val: str):
        """
        Method for setting directions - pretty straight forward. This model expects a single string value that includes
        newline characters to separate the arbitrary number of steps.
        """
        self._directions = val
