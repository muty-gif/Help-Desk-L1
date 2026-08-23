from datetime import datetime

from app.extensions import db


class Comment(db.Model):
    """Representa un comentario asociado a un ticket."""

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
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
        back_populates="comments"
    )

    user = db.relationship(
        "User",
        back_populates="comments"
    )