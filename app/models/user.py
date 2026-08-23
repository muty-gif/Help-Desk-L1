from app.extensions import db


class User(db.Model):
    """Representa a un usuario del sistema."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    created_tickets = db.relationship(
        "Ticket",
        foreign_keys="Ticket.user_id",
        back_populates="user"
    )

    assigned_tickets = db.relationship(
        "Ticket",
        foreign_keys="Ticket.technician_id",
        back_populates="technician"
    )

    comments = db.relationship(
        "Comment",
        back_populates="user"
    )

    history = db.relationship(
        "History",
        back_populates="user"
    )

    def __repr__(self):
        return f"<User {self.email}>"