from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from housechef.extensions import db
from ..mixins import Column, PkModel, relationship, TimestampMixin


class Household(PkModel, TimestampMixin):
    """Model for households, which are simple groupings of users"""

    __tablename__ = "households"

    """Columns"""
    name = Column(db.String(128), nullable=False, unique=True)

    """Relationships"""
    users = relationship("User", back_populates="household")
    recipes = relationship(
        "Recipe", back_populates="household", cascade="all, delete-orphan"
    )
    meals = relationship(
        "Meal", back_populates="household", cascade="all, delete-orphan"
    )
    shopping_list_items = relationship(
        "ShoppingList", back_populates="household", cascade="all, delete-orphan"
    )
    shopping_list = association_proxy("shopping_list_items", "ingredient")

    @hybrid_property
    def remaining_shopping_list_items(self):
        return [
            i.ingredient.name
            for i in self.shopping_list_items
            if i.still_needed is True
        ]

    def __repr__(self):
        return "<Household %s>" % self.name
