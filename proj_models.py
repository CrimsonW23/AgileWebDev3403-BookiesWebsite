from extensions import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), index=True, unique=True)
    password = db.Column(db.String(150), index=True, unique=False)
    email = db.Column(db.String(50), index=True, unique=True)
    currency = db.Column(db.Float, default=0.0, index=True)
    posts = db.relationship('Post', backref='user', lazy='dynamic')  # One-to-many relationship with Post
    joined_at   = db.Column(db.DateTime, default=datetime.utcnow,
                            server_default=db.func.now())
    
    profile_pic = db.Column(db.String(256), default="default.png")

    show_email  = db.Column(db.Boolean,
                            default=False,
                            server_default="0")

    def is_friends_with(self, other) -> bool:
        """Return True if self and other are already friends."""
        return db.session.execute(
            db.select(Friendship).where(
                (Friendship.user_id == self.id) &
                (Friendship.friend_id == other.id)
            )
        ).first() is not None

    def has_pending_with(self, other) -> bool:
        """Return True if a request is waiting between the two users."""
        return db.session.execute(
            db.select(FriendRequest).where(
                (FriendRequest.status == "pending") &
                (
                    ((FriendRequest.from_id == self.id) &
                     (FriendRequest.to_id   == other.id)) |
                    ((FriendRequest.from_id == other.id) &
                     (FriendRequest.to_id   == self.id))
                )
            )
        ).first() is not None

    def friends(self):
        """List of User objects who are friends with self."""
        friend_ids = db.session.scalars(
            db.select(Friendship.friend_id)
              .where(Friendship.user_id == self.id)
        ).all()
        if not friend_ids:
            return []
        return db.session.scalars(
            db.select(User).where(User.id.in_(friend_ids))
        ).all()

    def pending_requests(self):
        """Friend requests sent TO self that are still pending."""
        return db.session.scalars(
            db.select(FriendRequest)
              .where((FriendRequest.to_id == self.id) &
                     (FriendRequest.status == "pending"))
        ).all()
    

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
    
class FriendRequest(db.Model):
    __bind_key__ = "friends"        # ⇠ tells SQLAlchemy to use friends.db
    id       = db.Column(db.Integer, primary_key=True)
    from_id  = db.Column(db.Integer, nullable=False)
    to_id    = db.Column(db.Integer, nullable=False)
    status   = db.Column(db.String(10), default="pending")    # pending / accepted
    created  = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def sender(self):
        return User.query.get(self.from_id)

    @property
    def receiver(self):
        return User.query.get(self.to_id)

class Friendship(db.Model):
    __bind_key__ = "friends"
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, nullable=False)
    friend_id = db.Column(db.Integer, nullable=False)
