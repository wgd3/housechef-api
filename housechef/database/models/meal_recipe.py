from housechef.extensions import db


class MealRecipe(db.Model):
    __tablename__ = "meal_recipes"

    """Columns"""
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("recipes.id"), primary_key=True, nullable=False
    )
    meal_id = db.Column(
        db.Integer, db.ForeignKey("meals.id"), primary_key=True, nullable=False
    )

    """Relationships"""
    recipe = db.relationship("Recipe", lazy="joined")
    meal = db.relationship("Meal", back_populates="meal_recipes")

    def __init__(self, recipe=None, meal=None):
        self.recipe = recipe
        self.meal = meal
