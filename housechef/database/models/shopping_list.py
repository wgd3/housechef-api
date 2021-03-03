from flask import current_app
from sqlalchemy import event, func

from housechef.extensions import db


class ShoppingList(db.Model):
    __tablename__ = "shopping_lists"

    """Primary Keys"""
    household_id = db.Column(
        db.Integer, db.ForeignKey("households.id"), primary_key=True, nullable=False
    )
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredients.id"), primary_key=True, nullable=False
    )

    """Relationships"""
    ingredient = db.relationship("Ingredient", lazy="joined")
    household = db.relationship("Household", back_populates="shopping_list_items")

    """Extra Data"""
    time_created = db.Column(db.DateTime, default=func.now(), server_default=func.now())
    time_updated = db.Column(db.DateTime, onupdate=func.now())
    time_removed = db.Column(db.DateTime)
    still_needed = db.Column(db.Boolean, default=True)

    def __init__(self, ingredient=None, household=None):
        self.ingredient = ingredient
        self.household = household


@event.listens_for(ShoppingList.still_needed, "set")
def update_time_removed(target, value, oldvalue, initiator):
    """Update the time_removed when checked off"""
    if value is False and oldvalue is True:
        current_app.logger.debug(
            f"Marking {target.ingredient.name} off the shopping list!"
        )
        target.time_removed = func.now()
    elif value is True and oldvalue is False:
        current_app.logger.debug(
            f"Marking {target.ingredient.name} as back on the shopping list!"
        )
        target.time_removed = None
    db.session.add(target)
    db.session.commit()
