from housechef.extensions import db
from ..mixins import (
    Column,
    LookupByNameMixin,
    PkModel,
    reference_col,
    relationship,
    TimestampMixin,
)


class Tag(PkModel, TimestampMixin, LookupByNameMixin):
    """Model for 'tags' which allow for arbitrary grouping of recipes"""

    __tablename__ = "tags"
    __table_args__ = (
        db.UniqueConstraint("name", "user_id", name="_user_tag_constraint"),
    )

    """Columns"""
    # id
    # time_created
    # time_updated
    name = Column(db.String(128), unique=True, nullable=False)
    description = Column(db.String(128))
    public = Column(db.Boolean, default=False, nullable=False)

    """Relationships"""
    user = relationship("User", back_populates="tags")
    user_id = reference_col("users", nullable=True)

    recipes = relationship("RecipeTag", back_populates="tag")
