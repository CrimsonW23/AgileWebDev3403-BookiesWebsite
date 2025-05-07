from extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), index=True, unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(50), index=True, unique=True, nullable=False)
    currency = db.Column(db.Float, default=0.0, nullable=False)
    created_bets = db.relationship('CreatedBets', backref='creator', lazy=True)
    placed_bets = db.relationship('PlacedBets', backref='bettor', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True, unique=False)
    body = db.Column(db.String(150), index=True, unique=False)
    category = db.Column(db.String(25), index=True, unique=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now().replace(second=0, microsecond=0))
    author = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_post_user'), nullable=False)  # Named foreign key
    replies = db.relationship('Reply', backref='post', lazy='dynamic')  # One-to-many relationship with Reply

    def __repr__(self):
        return 'Post "{}"'.format(self.body)

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(150), index=True, unique=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now().replace(second=0, microsecond=0))
    author = db.Column(db.String(25), index=True, unique=False)  # Assuming author is a string for simplicity
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', name='fk_reply_post'), nullable=False)  # Named foreign key

    def __repr__(self):
        return 'Reply "{}"'.format(self.body)

class CreatedBets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    bet_type_description = db.Column(db.String(255), nullable=False)  # Descriptive bet type
    bet_type = db.Column(db.String(50), nullable=False)
    max_stake = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Interval, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_createdbets_user'), nullable=False)  # Named foreign key
    status = db.Column(db.String(20), nullable=False, default="upcoming")  
    

    def __repr__(self):
        return f"<CreatedBet {self.event_name} - {self.bet_type}>"

class ActiveBets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    bet_type_description = db.Column(db.String(255), nullable=False)  # Descriptive bet type
    bet_type = db.Column(db.String(50), nullable=False)
    max_stake = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Interval, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_activebets_user'), nullable=False)  # Named foreign key

    def __repr__(self):
        return f"<ActiveBet {self.event_name} - {self.bet_type}>"

class PlacedBets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_placedbets_user'), nullable=False)  # Named foreign key
    event_name = db.Column(db.String(100), nullable=False)
    bet_type_description = db.Column(db.String(255), nullable=False)  # Descriptive bet type
    bet_type = db.Column(db.String(50), nullable=False)  # Definitive bet type (e.g., "win" or "loss")
    stake_amount = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    potential_winnings = db.Column(db.Float, nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False, index=True)
    duration = db.Column(db.Interval, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="upcoming", index=True)   
    actual_winnings = db.Column(db.Float, nullable=True)
    date_settled = db.Column(db.DateTime, nullable=True)  

    def __repr__(self):
        return f"<PlacedBet {self.event_name} - {self.status}>"

class EventResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False, unique=True)
    outcome = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<EventResult {self.event_name} - {self.outcome}>"
