# Help Desk

Sistema de tickets de soporte construido con Flask.

Los usuarios crean incidencias, el equipo técnico las gestiona (estado,
prioridad y asignación) y cada cambio queda registrado en el historial
del ticket.

## Características

- **Autenticación** por sesión con contraseña encriptada (registro,
  inicio y cierre de sesión).
- **Dos roles**: `user` (crea y gestiona sus propios tickets) y
  `technician` (gestiona cualquier ticket).
- **Tickets** con título, descripción, categoría, prioridad y estado.
- **Comentarios** en cada ticket, visibles para su creador y para los
  técnicos.
- **Historial automático** de cambios de estado, prioridad, categoría,
  título y asignación de técnico.
- **Listado con filtros**: búsqueda por texto, estado y prioridad.
- **Panel de inicio** con estadísticas y los tickets más recientes.

## Estado del proyecto

Todo lo siguiente está implementado, probado y funcionando:

- [x] Esquema de base de datos con migraciones de Alembic y datos
  iniciales (`flask seed`).
- [x] Registro, inicio y cierre de sesión con contraseñas encriptadas
  (Werkzeug) y sesiones en servidor.
- [x] Ciclo de vida completo de un ticket: crear, consultar, editar y
  eliminar, con permisos comprobados en cada ruta.
- [x] Comentarios por ticket.
- [x] Gestión técnica: cambio de estado, cambio de prioridad,
  asignación **y desasignación** de técnico.
- [x] Historial automático de cambios con autor y valores anterior y
  nuevo.
- [x] Listado con búsqueda por texto y filtros de estado y prioridad,
  con visibilidad distinta según el rol.
- [x] Panel de inicio con estadísticas por estado, tickets sin asignar
  y últimos tickets.
- [x] Interfaz con Bootstrap 5: badges de estado/prioridad, formularios
  condicionados al rol y mensajes flash.
- [x] 51 pruebas automatizadas (`pytest`) y análisis estático (`ruff`)
  en verde.

## Reglas de permisos

| Acción | Creador | Técnico | Invitado |
| --- | --- | --- | --- |
| Ver el listado / su panel | ✔ (sus tickets) | ✔ (todos) | ✘ |
| Crear un ticket | ✔ | ✔ | ✘ |
| Ver y comentar un ticket | ✔ | ✔ | ✘ |
| Editar o eliminar el contenido | ✔ | ✘ | ✘ |
| Cambiar estado, prioridad o técnico | ✘ | ✔ | ✘ |

La regla es sencilla y está centralizada en `app/auth.py`
(`can_manage_ticket` y `owns_ticket`): **el creador es dueño del
contenido del ticket y los técnicos gestionan su flujo**.

## Cómo funciona un ticket

1. Un usuario crea un ticket: nace con el estado **Abierto**.
2. Un técnico lo toma, lo asigna a alguien del equipo y mueve su estado
   y prioridad según lo necesite.
3. El creador y los técnicos conversan en los comentarios.
4. El creador puede corregir título, descripción y categoría mientras
   el ticket existe, o eliminarlo.

Los estados semilla son *Abierto → En progreso → Pendiente → Resuelto →
Cerrado*. No hay una máquina de estados que restrinja las transiciones:
cualquier técnico puede llevar un ticket a cualquier estado, y esa
decisión queda registrada.

### Acciones que quedan en el historial

| Acción registrada | Quién la provoca |
| --- | --- |
| `Cambio de estado` | Técnico |
| `Cambio de prioridad` | Técnico |
| `Asignación de técnico` | Técnico (incluye desasignar) |
| `Edición de título` | Creador del ticket |
| `Cambio de categoría` | Creador del ticket |

## Cómo crear un técnico

No hay panel de administración todavía, así que el rol se asigna a
mano sobre la base de datos:

```bash
sqlite3 app/database/helpdesk.db \
  "UPDATE users SET role='technician' WHERE email='tu@correo.com';"
```

## Requisitos

- Python 3.10 o superior (probado con 3.14)
- pip

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Para trabajar con las pruebas:

```bash
pip install -r requirements-dev.txt
```

## Base de datos

Las migraciones crean el esquema y los estados/prioridades iniciales;
el comando `seed` añade además las categorías:

```bash
flask db upgrade
flask seed
```

El archivo SQLite se guarda en `app/database/helpdesk.db` y está
ignorado por git.

## Ejecutar la aplicación

```bash
flask run
```

o bien:

```bash
python run.py
```

## Pruebas

```bash
pytest
```

Hay 51 pruebas en `tests/`:

| Archivo | Qué cubre |
| --- | --- |
| `test_tickets.py` | Permisos de comentarios, estado y asignación |
| `test_auth.py` | Registro, login, logout y protección de rutas |
| `test_ticket_crud.py` | Crear, editar y eliminar tickets |
| `test_ticket_management.py` | Estado, prioridad y técnico (con historial) |
| `test_ticket_list.py` | Filtros, búsqueda, visibilidad y panel de inicio |

`tests/conftest.py` centraliza los fixtures: aplicación en memoria,
datos semilla y fábricas de usuarios y tickets.

## Calidad de código

```bash
ruff check app tests config.py run.py
```

## Configuración

Se puede sobreescribir mediante variables de entorno (o `.env`):

| Variable | Descripción | Por defecto |
| --- | --- | --- |
| `SECRET_KEY` | Clave secreta de la sesión | `dev-secret-key` |
| `DATABASE_URL` | Cadena de conexión de SQLAlchemy | SQLite local |

## Limitaciones conocidas

Cosas que el proyecto **todavía no hace**, para que nadie las busque en
vano:

- No hay rol de administración: no se crean técnicos desde la interfaz
  ni se gestionan categorías, estados o prioridades.
- No hay recuperación de contraseña ni verificación de correo.
- No hay notificaciones: nadie recibe aviso de que su ticket cambió.
- No hay adjuntos ni imágenes en los comentarios.
- No hay paginación: los listados cargan todos los tickets de golpe.
- El cierre de sesión es una petición `GET`, así que un enlace externo
  podría cerrar la sesión de alguien.
- La base de datos es SQLite: bien para desarrollo, pero hay que
  cambiar `DATABASE_URL` a PostgreSQL para concurrencia real.
- No hay configuración de despliegue (gunicorn, Docker, CI).

### Posibles siguientes pasos

1. Panel de administración (usuarios, técnicos y tablas de referencia).
2. Paginación y ordenación del listado.
3. Notificaciones por correo al cambiar el estado.
4. Recuperación de contraseña.
5. Logout por POST con token CSRF y expiración de sesión.

## Estructura

```
app/
  auth.py            # Sesión actual, decoradores de acceso y reglas de permisos
  extensions.py      # Instancias de SQLAlchemy y Flask-Migrate
  forms/             # Formularios WTForms (auth y tickets) y campos propios
  models/            # User, Ticket, Comment, History, Category, State, Priority
  routes/            # Blueprints: main (panel), auth, tickets
  seed.py            # Datos iniciales (comando `flask seed`)
  templates/         # Jinja2, con componentes reutilizables en templates/components
migrations/          # Migraciones de Alembic
tests/               # Pruebas con pytest (fixtures compartidos en conftest.py)
config.py            # Configuración de la aplicación
run.py               # Punto de entrada
pytest.ini           # Configuración de pytest
ruff.toml            # Reglas de lint
requirements.txt     # Dependencias de ejecución
requirements-dev.txt # Dependencias de desarrollo (pytest, ruff)
```

Cada ruta de tickets que modifica datos deja su entrada en
`History`, y las plantillas muestran ese historial ordenado del más
reciente al más antiguo.
