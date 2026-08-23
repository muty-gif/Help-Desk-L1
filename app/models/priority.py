from app.extensions import db


class Priority(db.Model):
    """Representa la prioridad del ticket."""

    __tablename__ = "priorities"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    tickets = db.relationship(
        "Ticket",
        back_populates="priority"
    )

    def __repr__(self):
        return f"<Priority {self.name}>"