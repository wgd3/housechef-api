from housechef.extensions import db


class UserRole(db.Model):
    __tablename__ = "user_roles"
    __table_args__ = (
        db.UniqueConstraint("user_id", "role_id", name="_user_role_constraint"),
    )

    """Primary Keys"""
    # Parent
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )
    # Child
    role_id = db.Column(
        db.Integer, db.ForeignKey("roles.id"), primary_key=True, nullable=False
    )

    """Relationships"""
    # Parent
    user = db.relationship("User", back_populates="user_roles")
    # Child
    role = db.relationship("Role", back_populates="users", lazy="joined")

    def __init__(self, role=None, user=None):
        self.role = role
        self.user = user

    def __repr__(self):
        return f"<UserRole - {self.user.username} has role {self.role.name}>"
