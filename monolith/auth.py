import functools
from flask_login import current_user, LoginManager
from monolith.gateway import get_getaway
from werkzeug.security import check_password_hash

login_manager = LoginManager()


class User:
    def __init__(self, id, is_operator, is_admin, is_health, password):
        self.id = id
        self._authenticated = False
        self.is_active = True
        self.is_operator = is_operator
        self.is_admin = is_admin
        self.is_health = is_health
        self.password = password

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id


def admin_required(func):
    @functools.wraps(func)
    def _admin_required(*args, **kw):
        admin = current_user.is_authenticated and current_user.is_admin
        if not admin:
            return login_manager.unauthorized()
        return func(*args, **kw)

    return _admin_required


def health_authority_required(func):
    @functools.wraps(func)
    def _health_authority_required(*args, **kw):
        authority = current_user.is_authenticated and current_user.is_health_authority
        if not authority:
            return login_manager.unauthorized()
        return func(*args, **kw)

    return _health_authority_required


def operator_required(func):
    @functools.wraps(func)
    def _operator_required(*args, **kw):
        try:
            if not current_user.is_operator:
                return login_manager.unauthorized()
        except:
            return login_manager.unauthorized()
        return func(*args, **kw)

    return _operator_required


@login_manager.user_loader
def load_user(user_id):
    user, status = get_getaway().get_user(user_id)
    if status == 200:
        user._authenticated = True
        return user
    else:
        return None
