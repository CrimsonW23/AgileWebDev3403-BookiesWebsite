from extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), index=True, unique=True)
    password = db.Column(db.String(150), index=True, unique=False)
    email = db.Column(db.String(50), index=True, unique=True)

    def __repr__(self):
        return 'User {}'.format(self.username)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True, unique=False)
    body = db.Column(db.String(150), index=True, unique=False)
    category = db.Column(db.String(25), index=True, unique=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now().replace(second=0, microsecond=0))
    author = db.Column(db.String(25), index=True, unique=False)  # Assuming author is a string for simplicity
    replies = db.relationship('Reply', backref='post', lazy='dynamic')  # One-to-many relationship with Reply

    def __repr__(self):
        return 'Post "{}"'.format(self.body)
    
class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(150), index=True, unique=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now().replace(second=0, microsecond=0))
    author = db.Column(db.String(25), index=True, unique=False)  # Assuming author is a string for simplicity
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))  # Foreign key to Post

    def __repr__(self):
        return 'Reply "{}"'.format(self.body)
