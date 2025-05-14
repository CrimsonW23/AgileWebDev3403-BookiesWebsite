import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_BINDS = {
        "friends": (
            os.environ.get("FRIENDS_DATABASE_URL")
            or f"sqlite:///{os.path.join(basedir, 'friends.db')}"
        )
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = "static/uploads/avatars"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
