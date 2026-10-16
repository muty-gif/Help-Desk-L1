from datetime import UTC, datetime

from app.extensions import db


class History(db.Model):
    """Representa un cambio realizado sobre un ticket."""

    __tablename__ = "history"

    id = db.Column(db.Integer, primary_key=True)

    action = db.Column(
        db.String(50),
        nullable=False
    )

    old_value = db.Column(
        db.String(255),
        nullable=True
    )

    new_value = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("tickets.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    ticket = db.relationship(
        "Ticket",
        back_populates="history"
    )

    user = db.relationship(
        "User",
        back_populates="history"
    )