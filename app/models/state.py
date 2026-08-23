from app.extensions import db


class State(db.Model):
    """Representa el estado del ticket."""

    __tablename__ = "states"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    tickets = db.relationship(
        "Ticket",
        back_populates="status"
    )

    def __repr__(self):
        return f"<State {self.name}>"