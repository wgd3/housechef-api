from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from housechef.extensions import db
from ..mixins import (
    Column,
    LookupByNameMixin,
    PkModel,
    reference_col,
    relationship,
    TimestampMixin,
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
    notes = relationship("Note", back_populates="recipe", cascade="all, delete-orphan")

    """Relationships with association proxies"""
    recipe_diet_types = relationship(
        "RecipeDietType",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    diets = association_proxy("recipe_diet_types", "diet_type")

    recipe_cuisines = relationship(
        "RecipeCuisine", back_populates="recipe", cascade="all, delete-orphan"
    )
    cuisines = association_proxy("recipe_cuisines", "cuisine")

    recipe_dish_types = relationship(
        "RecipeDishType", back_populates="recipe", cascade="all, delete-orphan"
    )
    dish_types = association_proxy("recipe_dish_types", "dish_type")

    ingredients = relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan"
    )
    tags = relationship(
        "RecipeTag", back_populates="recipe", cascade="all, delete-orphan"
    )

    # meals = relationship(
    #     "MealRecipe", back_populates="recipe", cascade="all, delete-orphan"
    # )

    def __repr__(self):
        return f"<Recipe #{self.id} - {self.name}>"

    @hybrid_property
    def calories(self):
        return round(
            sum([i.calories for i in self.ingredients if i.calories is not None]), 0
        )

    @hybrid_property
    def fat(self):
        return round(sum([i.fat for i in self.ingredients if i.fat is not None]), 1)

    @hybrid_property
    def protein(self):
        return round(
            sum([i.protein for i in self.ingredients if i.protein is not None]), 1
        )

    @hybrid_property
    def carbohydrates(self):
        return round(
            sum(
                [
                    i.carbohydrates
                    for i in self.ingredients
                    if i.carbohydrates is not None
                ]
            ),
            1,
        )

    @hybrid_property
    def net_carbohydrates(self):
        return round(
            sum(
                [
                    i.net_carbohydrates
                    for i in self.ingredients
                    if i.net_carbohydrates is not None
                ]
            ),
            1,
        )

    @hybrid_property
    def sodium(self):
        return round(
            sum([i.sodium for i in self.ingredients if i.sodium is not None]), 1
        )

    @hybrid_property
    def fiber(self):
        return round(sum([i.fiber for i in self.ingredients if i.fiber is not None]), 1)

    @property
    def slug(self) -> str:
        return self.name.lower().replace(" ", "-")

    @property
    def macros(self):
        return {
            "calories": self.calories,
            "fat": self.fat,
            "protein": self.protein,
            "carbohydrates": self.carbohydrates,
            "net_carbohydrates": self.net_carbohydrates,
        }

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
