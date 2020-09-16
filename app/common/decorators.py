from flask_login import current_user
from flask import redirect, url_for, request
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.user_name == 'Guest':
            return redirect(url_for('users.login', next=request.url))
        elif current_user.is_authenticated:
            pass
        else:
            return redirect(url_for('index', next=request.url))
        return f(*args, **kwargs)

    return decorated_function



