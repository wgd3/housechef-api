from housechef.extensions import db


class RecipeCuisine(db.Model):
    """Association Table for many-to-many relationships for recipes and cuisines"""

    __tablename__ = "recipe_cuisines"
    __table_args__ = (
        db.UniqueConstraint(
            "recipe_id", "cuisine_id", name="_recipe_cuisine_constraint"
        ),
    )

    """Columns"""
    # Parent
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("recipes.id"), primary_key=True, nullable=False
    )
    # Child
    cuisine_id = db.Column(
        db.Integer, db.ForeignKey("cuisines.id"), primary_key=True, nullable=False
    )

    """Relationships"""
    # Parent
    recipe = db.relationship("Recipe", back_populates="recipe_cuisines")
    # Child
    cuisine = db.relationship("Cuisine", back_populates="recipes", lazy="joined")

    def __init__(self, cuisine=None, recipe=None):
        """Called when appending Cuisine objects to Recipe objects, child used as first arg"""
        self.cuisine = cuisine
        self.recipe = recipe

    def __repr__(self):
        return f"<RecipeCuisine - {self.cuisine.name}/{self.recipe.name}>"
