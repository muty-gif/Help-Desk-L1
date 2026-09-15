from flask import Blueprint, redirect, abort, render_template, url_for

from app.auth import get_current_user, login_required, role_required
from app.extensions import db

from app.forms.ticket import (
    CommentForm, 
    TechnicianForm,
    TicketForm, 
    TicketStateForm
)

from app.models import Category, Comment, History, Priority, State, Ticket, User


tickets_bp = Blueprint(
    "tickets",
    __name__,
    url_prefix="/tickets"
)


@tickets_bp.route("/")
@login_required
def index():
    current_user = get_current_user()

    if current_user.role == "technician":
        tickets = Ticket.query.order_by(
            Ticket.created_at.desc()
        ).all()
    else:
        tickets = Ticket.query.filter_by(
            user_id=current_user.id
        ).order_by(
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

@tickets_bp.route("/<int:ticket_id>")
@login_required
def detail(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)

    current_user = get_current_user()

    if (
        current_user.role != "technician"
        and ticket.user_id != current_user.id
    ):
        abort(403)

    state_form = TicketStateForm()

    state_form.state_id.choices = [
        (state.id, state.name)
        for state in State.query.order_by(State.id).all()
    ]

    comment_form = CommentForm()

    technician_form = TechnicianForm()

    technician_form.technician_id.choices = [
        (user.id, user.name)
        for user in User.query.order_by(User.name).all()
    ]
    
    return render_template(
        "tickets/detail.html",
        ticket=ticket,
        state_form=state_form,
        comment_form=comment_form,
        technician_form=technician_form
    )

@tickets_bp.route("/<int:ticket_id>/state", methods=["POST"])
@login_required
@role_required("technician")
def change_state(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)

    form = TicketStateForm()

    form.state_id.choices = [
        (state.id, state.name)
        for state in State.query.order_by(State.id).all()
    ]

    if form.validate_on_submit():
        current_user = get_current_user()

        old_state = ticket.state
        new_state = db.get_or_404(State, form.state_id.data)

        if old_state.id != new_state.id:
            history = History(
                action="Cambio de estado",
                old_value=old_state.name,
                new_value=new_state.name,
                ticket_id=ticket.id,
                user_id=current_user.id
            )

            ticket.state = new_state

            db.session.add(history)
            db.session.commit()

    return redirect(
        url_for("tickets.detail", ticket_id=ticket.id)
    )

@tickets_bp.route("/<int:ticket_id>/comments", methods=["POST"])
@login_required
def add_comment(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)

    current_user = get_current_user()

    if (
        current_user.role != "technician"
        and ticket.user_id != current_user.id
    ):
        abort(403)

    form = CommentForm()

    if form.validate_on_submit():
        current_user = get_current_user()

        comment = Comment(
            content=form.content.data.strip(),
            ticket_id=ticket.id,
            user_id=current_user.id
        )

        db.session.add(comment)
        db.session.commit()

    return redirect(
        url_for("tickets.detail", ticket_id=ticket.id)
    )

@tickets_bp.route(
    "/<int:ticket_id>/technician",
    methods=["POST"]
)
@login_required
@role_required("technician")
def assign_technician(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)

    form = TechnicianForm()

    form.technician_id.choices = [
        (user.id, user.name)
        for user in User.query.order_by(User.name).all()
    ]

    if form.validate_on_submit():
        current_user = get_current_user()

        old_technician = ticket.technician
        new_technician = db.get_or_404(
            User,
            form.technician_id.data
        )

        if old_technician != new_technician:

            old_value = (
                old_technician.name
                if old_technician
                else "Sin asignar"
            )

            history = History(
                action="Asignación de técnico",
                old_value=old_value,
                new_value=new_technician.name,
                ticket_id=ticket.id,
                user_id=current_user.id
            )

            ticket.technician = new_technician

            db.session.add(history)
            db.session.commit()

    return redirect(
        url_for("tickets.detail", ticket_id=ticket.id)
    )