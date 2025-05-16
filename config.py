import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()

class Config(object):

    SECRET_KEY = os.getenv('SECRET_KEY')

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

class TestingConfig(object):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False
    
    SQLALCHEMY_BINDS = {
        "friends": (
            os.environ.get("FRIENDS_DATABASE_URL")
            or f"sqlite:///{os.path.join(basedir, 'friends.db')}"
        )
    }