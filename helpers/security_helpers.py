"""
This helper file contains functions that we will use for
security purposes.
"""
from functools import wraps
from flask import redirect, session

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def login_required(arg):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(arg)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return arg(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Checks if the extension of the given file is in ALLOWED_EXTENSIONS"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
