from .home import home
from .auth import auth
from .users import users
from .restaurants import restaurants
from .contact_tracing import contact_tracing


blueprints = [home, auth, users, restaurants, contact_tracing]
