from extensions import db
from datetime import datetime 
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)  
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)  
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(10), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    currency = db.Column(db.Float, default=0.0, index=True)  
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)  
    created_bets = db.relationship('CreatedBets', backref='creator', lazy=True)
    placed_bets = db.relationship('PlacedBets', backref='bettor', lazy=True)
    active = db.Column(db.Boolean, default=True)  # For Flask-Login
    profile_pic = db.Column(db.String(256), default="default.png")
    show_email  = db.Column(db.Boolean,
                            default=False,
                            server_default="0")
    show_stats = db.Column(db.Boolean, default=False, server_default="0")
    show_bets  = db.Column(db.Boolean, default=False, server_default="0")

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check the hashed password."""
        return check_password_hash(self.password, password)
    
    
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
       
    # Properties required by Flask-Login
    @property
    def is_active(self):
        return self.active
        
    @property
    def is_authenticated(self):
        return True
        
    @property
    def is_anonymous(self):
        return False
        
    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<User {self.username}>"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True, unique=False)
    body = db.Column(db.String(150), index=True, unique=False)
    category = db.Column(db.String(25), index=True, unique=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now().replace(second=0, microsecond=0))
    
    # Foreign key references User.id
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='posts')

    replies = db.relationship('Reply', backref='post', lazy='dynamic')
    privacy = db.Column(db.String(10), nullable=False, default='public') 
    
    @property
    def most_recent_reply(self):
        if self.replies.count() == 0:
            return self
        return self.replies.order_by(Reply.timestamp.desc()).first()

    def __repr__(self):
        return f'Post "{self.body}"'

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(150), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now().replace(second=0, microsecond=0))

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='replies')

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return f'Reply "{self.body}"'

class CreatedBets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    bet_type_description = db.Column(db.String(255), nullable=False) 
    bet_type = db.Column(db.String(50), nullable=False)
    max_stake = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Interval, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_createdbets_user'), nullable=False) 
    status = db.Column(db.String(20), nullable=False, default="upcoming")  
    

    def __repr__(self):
        return f"<CreatedBet {self.event_name} - {self.bet_type}>"

class ActiveBets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    bet_type_description = db.Column(db.String(255), nullable=False) 
    bet_type = db.Column(db.String(50), nullable=False)
    max_stake = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Interval, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_activebets_user'), nullable=False) 

    def __repr__(self):
        return f"<ActiveBet {self.event_name} - {self.bet_type}>"

class PlacedBets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_placedbets_user'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('active_bets.id', name='fk_placed_bets_game_id'), nullable=False)
    event_name = db.Column(db.String(100), nullable=False)
    bet_type_description = db.Column(db.String(255), nullable=False)
    bet_type = db.Column(db.String(50), nullable=False)
    stake_amount = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    potential_winnings = db.Column(db.Float, nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False, index=True)
    duration = db.Column(db.Interval, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="upcoming", index=True)
    actual_winnings = db.Column(db.Float, nullable=True)
    date_settled = db.Column(db.DateTime, nullable=True)
    event_outcome = db.Column(db.String(50), nullable=True)   

    def __repr__(self):
        return f"<PlacedBet {self.event_name} - {self.status}>"

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
