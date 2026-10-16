from werkzeug.security import check_password_hash, generate_password_hash

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

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="user"
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

    def set_password(self, password):
        """Genera y almacena el hash de una contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Comprueba una contraseña contra el hash almacenado."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"