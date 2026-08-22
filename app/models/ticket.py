from datetime import datetime

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
        default=datetime.utcnow
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    category = db.relationship(
        "Category",
        backref="tickets"
    )

    status_id = db.Column(
        db.Integer,
        db.ForeignKey("states.id"),
        nullable=False
    )

    status = db.relationship(
        "State",
        backref="tickets"
    )

    def __repr__(self):
        return f"<Ticket {self.id}>"