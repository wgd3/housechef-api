from housechef.extensions import db


class UserRole(db.Model):
    __tablename__ = "user_roles"
    __table_args__ = (
        db.UniqueConstraint("user_id", "role_id", name="_user_role_constraint"),
    )

    """Primary Keys"""
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False
    )
    role_id = db.Column(
        db.Integer, db.ForeignKey("roles.id"), primary_key=True, nullable=False
    )

    """Relationships"""
    user = db.relationship("User", back_populates="roles")
    role = db.relationship("Role", back_populates="users")

    def __repr__(self):
        return f"<UserRole - {self.user.username} has role {self.role.name}>"
