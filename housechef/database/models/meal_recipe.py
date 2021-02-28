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
    recipe = db.relationship("Recipe", back_populates="meals")
    meal = db.relationship("Meal", back_populates="recipes")
