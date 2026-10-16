from datetime import UTC, datetime

from app.extensions import db


class Ticket(db.Model):
    """Representa una incidencia o ticket de soporte."""

    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    category = db.relationship(
        "Category",
        back_populates="tickets"
    )

    state_id = db.Column(
        db.Integer,
        db.ForeignKey("states.id"),
        nullable=False
    )

    state = db.relationship(
        "State",
        back_populates="tickets"
    )

    priority_id = db.Column(
        db.Integer,
        db.ForeignKey("priorities.id"),
        nullable=False
    )

    priority = db.relationship(
        "Priority",
        back_populates="tickets"
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    
    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="created_tickets"
    )
    
    technician_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )
    
    technician = db.relationship(
        "User",
        foreign_keys=[technician_id],
        back_populates="assigned_tickets"
    )

    comments = db.relationship(
        "Comment",
        back_populates="ticket",
        cascade="all, delete-orphan"
    )

    history = db.relationship(
        "History",
        back_populates="ticket",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Ticket {self.id}>"