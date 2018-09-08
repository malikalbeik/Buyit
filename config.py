import os
from tempfile import mkdtemp
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'buyit.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/photos'
    UPLOAD_FOLDER_AVATAR = 'static/user-avatar'
    CATEGORIES = ["cars", "tech", "motors", "furniture", "entertainment", "clothing", "other"]
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True

    # Configure session to use filesystem (instead of signed cookies)
    SESSION_FILE_DIR = mkdtemp()
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
