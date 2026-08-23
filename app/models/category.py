from app.extensions import db


class Category(db.Model):
    """Representa una categoría de tickets."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    tickets = db.relationship(
        "Ticket",
        back_populates="category"
    )

    def __repr__(self):
        return f"<Category {self.name}>"