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
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("recipes.id"), primary_key=True, nullable=False
    )
    cuisine_id = db.Column(
        db.Integer, db.ForeignKey("cuisines.id"), primary_key=True, nullable=False
    )

    """Relationships"""
    recipe = db.relationship("Recipe", back_populates="cuisines")
    cuisine = db.relationship("Cuisine", back_populates="recipes")

    def __repr__(self):
        return f"<RecipeCuisine - {self.cuisine.name}/{self.recipe.name}>"
