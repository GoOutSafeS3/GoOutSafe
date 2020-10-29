import functools
from flask_login import current_user, LoginManager
from monolith.database import User


login_manager = LoginManager()


def admin_required(func):
    @functools.wraps(func)
    def _admin_required(*args, **kw):
        admin = current_user.is_authenticated and current_user.is_admin
        if not admin:
            return login_manager.unauthorized()
        return func(*args, **kw)
    return _admin_required

def health_auyhority_required(func):
    @functools.wraps(func)
    def _health_auyhority_required(*args, **kw):
        authority = current_user.is_authenticated and current_user.is_health_authority
        if not authority:
            return login_manager.unauthorized()
        return func(*args, **kw)
    return _health_auyhority_required


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

def is_admin():
    if current_user.is_anonymous is True:
        return login_manager.unauthorized()
    if current_user.is_admin:
        return True
    else:
        return login_manager.unauthorized()


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user is not None:
        user._authenticated = True
    return user
