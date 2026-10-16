from flask import Blueprint, render_template
from sqlalchemy import func

from app.auth import get_current_user
from app.extensions import db
from app.models import State, Ticket

main_bp = Blueprint("main", __name__)


def _ticket_stats(user):
    """Agrupa los tickets visibles para el usuario por estado."""
    query = db.session.query(
        State.name,
        func.count(Ticket.id)
    ).join(
        Ticket,
        Ticket.state_id == State.id
    )

    if user.role != "technician":
        query = query.filter(Ticket.user_id == user.id)

    return dict(query.group_by(State.name).all())


def _unassigned_count(user):
    """Cuenta los tickets sin técnico asignado en el alcance del usuario."""
    query = db.session.query(func.count(Ticket.id)).filter(
        Ticket.technician_id.is_(None)
    )

    if user.role != "technician":
        query = query.filter(Ticket.user_id == user.id)

    return query.scalar()


@main_bp.route("/")
def index():
    user = get_current_user()

    if user is None:
        return render_template("index.html")

    if user.role == "technician":
        recent = Ticket.query.order_by(
            Ticket.created_at.desc()
        ).limit(5).all()
    else:
        recent = Ticket.query.filter_by(
            user_id=user.id
        ).order_by(
            Ticket.created_at.desc()
        ).limit(5).all()

    stats = _ticket_stats(user)

    return render_template(
        "index.html",
        stats=stats,
        total=sum(stats.values()),
        unassigned=_unassigned_count(user),
        recent=recent
    )
