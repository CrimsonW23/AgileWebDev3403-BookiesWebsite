from extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), index=True, unique=True)
    password = db.Column(db.String(150), index=True, unique=False)
    email = db.Column(db.String(50), index=True, unique=True)
    currency = db.Column(db.Float, default=0.0, index=True)
    posts = db.relationship('Post', backref='user', lazy='dynamic')  # One-to-many relationship with Post

    def __repr__(self):
        return 'User {}'.format(self.username)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True, unique=False)
    body = db.Column(db.String(150), index=True, unique=False)
    category = db.Column(db.String(25), index=True, unique=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now().replace(second=0, microsecond=0))
    author = db.Column(db.Integer, db.ForeignKey('user.id'))  # Foreign key to User
    replies = db.relationship('Reply', backref='post', lazy='dynamic')  # One-to-many relationship with Reply
    
    @property
    def most_recent_reply(self):
        if self.replies.count() == 0:
            return self
        return self.replies.order_by(Reply.timestamp.desc()).first()

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

class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_name = db.Column(db.String(100), nullable=False)  # Name of the event
    bet_type = db.Column(db.String(50), nullable=False)  # User's bet type (e.g., "win" or "loss")
    stake_amount = db.Column(db.Float, nullable=False)  # Amount the user bet
    odds = db.Column(db.Float, nullable=False)  # Odds for the bet
    potential_winnings = db.Column(db.Float, nullable=False)  # Potential winnings
    actual_winnings = db.Column(db.Float, nullable=True)  # Winnings after the event
    scheduled_time = db.Column(db.DateTime, nullable=False)  # When the event is scheduled
    duration = db.Column(db.Integer, nullable=False)  # Duration in hours
    status = db.Column(db.String(50), nullable=False, default="Upcoming")  # Bet status: Upcoming, Ongoing, Completed
    event_outcome = db.Column(db.String(50), nullable=True)  # Outcome of the event (e.g., "win" or "loss")
    date_settled = db.Column(db.DateTime, nullable=True)  # When the bet was settled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When the bet was created

    def __repr__(self):
        return f"<Bet {self.event_name} - {self.status}>"

class ActiveBets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)  # Name of the event
    bet_type = db.Column(db.String(50), nullable=False)  # User's bet type (e.g., "win" or "loss")
    stake_amount = db.Column(db.Float, nullable=False)  # Highest amount the user can bet
    odds = db.Column(db.Float, nullable=False)  # Odds for the bet
    scheduled_time = db.Column(db.DateTime, nullable=False)  # When the event is scheduled
    duration = db.Column(db.Integer, nullable=False)  # Duration in hours
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When the bet was created

    def __repr__(self):
        return f"<Bet {self.event_name} - {self.bet_type}>"

class EventResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False, unique=True)   
    outcome = db.Column(db.String(50), nullable=False)   
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)   

    def __repr__(self):
        return f"<EventResult {self.event_name} - {self.outcome}>"
