from housechef.extensions import db


class RecipeTag(db.Model):

    __tablename__ = "recipe_tags"
    __table_args__ = (
        db.UniqueConstraint("recipe_id", "tag_id", name="_recipe_tag_constraint"),
    )

    """Columns"""
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("recipes.id"), primary_key=True, nullable=False
    )
    tag_id = db.Column(
        db.Integer, db.ForeignKey("tags.id"), primary_key=True, nullable=False
    )

    """Relationships"""
    recipe = db.relationship("Recipe", back_populates="tags")
    tag = db.relationship("Tag", back_populates="recipes")

    def __repr__(self):
        return f"<RecipeTag {self.tag.name} on {self.recipe.name}>"
