from housechef.extensions import db
from ..mixins import (
    Column,
    LookupByNameMixin,
    PkModel,
    TimestampMixin,
    reference_col,
    relationship,
)


class Role(PkModel, TimestampMixin):
    __tablename__ = "roles"

    """Columns"""
    name = Column(db.String, nullable=False, unique=True)
    default = Column(db.Boolean, nullable=False, default=False)

    """Relationships"""
    users = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Role {self.name}>"
