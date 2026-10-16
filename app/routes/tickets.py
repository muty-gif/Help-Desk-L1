from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.auth import (
    can_manage_ticket,
    get_current_user,
    login_required,
    owns_ticket,
    role_required,
)
from app.extensions import db
from app.forms.ticket import (
    CommentForm,
    TechnicianForm,
    TicketEditForm,
    TicketFilterForm,
    TicketForm,
    TicketPriorityForm,
    TicketStateForm,
)
from app.models import (
    Category,
    Comment,
    History,
    Priority,
    State,
    Ticket,
    User,
)

tickets_bp = Blueprint(
    "tickets",
    __name__,
    url_prefix="/tickets"
)

#: Valor del select "Sin asignar" en el formulario de técnico.
NO_TECHNICIAN = 0


def _category_choices():
    """Opciones del selector de categorías."""
    return [
        (category.id, category.name)
        for category in Category.query.order_by(Category.name).all()
    ]

def _priority_choices():
    """Opciones del selector de prioridades."""
    return [
        (priority.id, priority.name)
        for priority in Priority.query.order_by(Priority.id).all()
    ]

def _state_choices():
    """Opciones del selector de estados."""
    return [
        (state.id, state.name)
        for state in State.query.order_by(State.id).all()
    ]

def _technician_choices():
    """Opciones del selector de técnicos, con la opción de desasignar."""
    technicians = User.query.filter_by(
        role="technician"
    ).order_by(User.name).all()

    return [
        (NO_TECHNICIAN, "Sin asignar")
    ] + [
        (user.id, user.name)
        for user in technicians
    ]


@tickets_bp.route("/")
@login_required
def index():
    current_user = get_current_user()

    filter_form = TicketFilterForm(request.args)

    filter_form.state_id.choices = [
        (0, "Todos")
    ] + _state_choices()

    filter_form.priority_id.choices = [
        (0, "Todas")
    ] + _priority_choices()

    query = Ticket.query

    # Cada usuario solo ve sus propios tickets; los técnicos ven todos.
    if current_user.role != "technician":
        query = query.filter(
            Ticket.user_id == current_user.id
        )

    if filter_form.state_id.data:
        query = query.filter(
            Ticket.state_id == filter_form.state_id.data
        )

    if filter_form.priority_id.data:
        query = query.filter(
            Ticket.priority_id == filter_form.priority_id.data
        )

    term = (filter_form.q.data or "").strip()

    if term:
        pattern = f"%{term}%"

        query = query.filter(
            db.or_(
                Ticket.title.ilike(pattern),
                Ticket.description.ilike(pattern)
            )
        )

    tickets = query.order_by(
        Ticket.created_at.desc()
    ).all()

    return render_template(
        "tickets/index.html",
        tickets=tickets,
        filter_form=filter_form
    )


@tickets_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = TicketForm()

    form.category_id.choices = _category_choices()
    form.priority_id.choices = _priority_choices()

    if form.validate_on_submit():
        current_user = get_current_user()

        open_state = State.query.filter_by(
            name="Abierto"
        ).first()

        if open_state is None:
            flash(
                "No hay estados configurados. "
                "Ejecuta el comando `flask seed`.",
                "danger"
            )
        else:
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

            flash(
                "Ticket creado correctamente.",
                "success"
            )

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

    if not can_manage_ticket(current_user, ticket):
        abort(403)

    state_form = TicketStateForm()

    state_form.state_id.choices = _state_choices()

    priority_form = TicketPriorityForm()

    priority_form.priority_id.choices = _priority_choices()

    comment_form = CommentForm()

    technician_form = TechnicianForm()

    technician_form.technician_id.choices = _technician_choices()

    return render_template(
        "tickets/detail.html",
        ticket=ticket,
        state_form=state_form,
        priority_form=priority_form,
        comment_form=comment_form,
        technician_form=technician_form,
        is_owner=owns_ticket(current_user, ticket)
    )

@tickets_bp.route("/<int:ticket_id>/edit", methods=["GET", "POST"])
@login_required
def edit(ticket_id):
    """Permite al creador del ticket corregir su contenido."""
    ticket = db.get_or_404(Ticket, ticket_id)

    current_user = get_current_user()

    if not owns_ticket(current_user, ticket):
        abort(403)

    form = TicketEditForm(obj=ticket)

    form.category_id.choices = _category_choices()

    if form.validate_on_submit():
        old_title = ticket.title
        old_category = ticket.category

        new_title = form.title.data.strip()
        new_category = db.session.get(
            Category,
            form.category_id.data
        )

        if new_category is None:
            abort(404)

        if new_title != old_title:
            db.session.add(History(
                action="Edición de título",
                old_value=old_title,
                new_value=new_title,
                ticket_id=ticket.id,
                user_id=current_user.id
            ))

        if new_category != old_category:
            db.session.add(History(
                action="Cambio de categoría",
                old_value=old_category.name,
                new_value=new_category.name,
                ticket_id=ticket.id,
                user_id=current_user.id
            ))

        ticket.title = new_title
        ticket.description = form.description.data.strip()
        ticket.category = new_category

        db.session.commit()

        flash(
            "Ticket actualizado correctamente.",
            "success"
        )

        return redirect(
            url_for("tickets.detail", ticket_id=ticket.id)
        )

    return render_template(
        "tickets/edit.html",
        form=form,
        ticket=ticket
    )

@tickets_bp.route("/<int:ticket_id>/delete", methods=["POST"])
@login_required
def delete(ticket_id):
    """Elimina un ticket creado por el usuario actual."""
    ticket = db.get_or_404(Ticket, ticket_id)

    current_user = get_current_user()

    if not owns_ticket(current_user, ticket):
        abort(403)

    db.session.delete(ticket)
    db.session.commit()

    flash(
        "Ticket eliminado correctamente.",
        "success"
    )

    return redirect(
        url_for("tickets.index")
    )

@tickets_bp.route("/<int:ticket_id>/state", methods=["POST"])
@login_required
@role_required("technician")
def change_state(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)

    form = TicketStateForm()

    form.state_id.choices = _state_choices()

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

            flash(
                f"Estado cambiado a {new_state.name}.",
                "success"
            )

    return redirect(
        url_for("tickets.detail", ticket_id=ticket.id)
    )

@tickets_bp.route("/<int:ticket_id>/priority", methods=["POST"])
@login_required
@role_required("technician")
def change_priority(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)

    form = TicketPriorityForm()

    form.priority_id.choices = _priority_choices()

    if form.validate_on_submit():
        current_user = get_current_user()

        old_priority = ticket.priority
        new_priority = db.get_or_404(
            Priority,
            form.priority_id.data
        )

        if old_priority.id != new_priority.id:
            history = History(
                action="Cambio de prioridad",
                old_value=old_priority.name,
                new_value=new_priority.name,
                ticket_id=ticket.id,
                user_id=current_user.id
            )

            ticket.priority = new_priority

            db.session.add(history)
            db.session.commit()

            flash(
                f"Prioridad cambiada a {new_priority.name}.",
                "success"
            )

    return redirect(
        url_for("tickets.detail", ticket_id=ticket.id)
    )

@tickets_bp.route("/<int:ticket_id>/comments", methods=["POST"])
@login_required
def add_comment(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)

    current_user = get_current_user()

    if not can_manage_ticket(current_user, ticket):
        abort(403)

    form = CommentForm()

    if form.validate_on_submit():
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

    form.technician_id.choices = _technician_choices()

    if form.validate_on_submit():
        current_user = get_current_user()

        old_technician = ticket.technician

        if form.technician_id.data == NO_TECHNICIAN:
            new_technician = None
            new_value = "Sin asignar"
        else:
            new_technician = db.get_or_404(
                User,
                form.technician_id.data
            )
            new_value = new_technician.name

        if old_technician != new_technician:
            old_value = (
                old_technician.name
                if old_technician
                else "Sin asignar"
            )

            history = History(
                action="Asignación de técnico",
                old_value=old_value,
                new_value=new_value,
                ticket_id=ticket.id,
                user_id=current_user.id
            )

            ticket.technician = new_technician

            db.session.add(history)
            db.session.commit()

            if new_technician is None:
                message = "Técnico desasignado del ticket."
            else:
                message = f"Técnico asignado: {new_value}."

            flash(message, "success")

    return redirect(
        url_for("tickets.detail", ticket_id=ticket.id)
    )
