from flask import Blueprint, redirect, render_template, url_for

from app.auth import get_current_user, login_required
from app.extensions import db
from app.forms.ticket import TicketForm
from app.models import Category, Priority, State, Ticket


tickets_bp = Blueprint(
    "tickets",
    __name__,
    url_prefix="/tickets"
)


@tickets_bp.route("/")
@login_required
def index():
    tickets = Ticket.query.order_by(
        Ticket.created_at.desc()
    ).all()

    return render_template(
        "tickets/index.html",
        tickets=tickets
    )


@tickets_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = TicketForm()

    form.category_id.choices = [
        (category.id, category.name)
        for category in Category.query.order_by(Category.name).all()
    ]

    form.priority_id.choices = [
        (priority.id, priority.name)
        for priority in Priority.query.order_by(Priority.id).all()
    ]

    if form.validate_on_submit():
        current_user = get_current_user()

        open_state = State.query.filter_by(
            name="Abierto"
        ).first()

        ticket = Ticket(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            category_id=form.category_id.data,
            priority_id=form.priority_id.data,
            state_id=open_state.id,
            user_id=current_user.id
        )

        db.session.add(ticket)
        db.session.commit()

        return redirect(
            url_for("tickets.index")
        )

    return render_template(
        "tickets/create.html",
        form=form
    )