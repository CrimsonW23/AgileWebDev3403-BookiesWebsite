from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import PostForm, ReplyForm, CreateBetForm, PlaceBetForm
from datetime import datetime, timedelta
from extensions import db
from proj_models import User, Post, Reply, EventResult, PlacedBets, CreatedBets, ActiveBets
import os 
from sqlalchemy import func

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = '9f8c1e6e49b4d9e6b2c442a1a8f3ecb1' #Session id used for testing

db.init_app(app)
migrate = Migrate(app, db)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

def fetch_event_outcome(event_name):
    """Simulate fetching the event outcome."""
    simulated_outcomes = {
        "Real Madrid vs Barcelona": "win",
        "FIFA World Cup Final": "loss",
        "AFL: Fremantle vs. West Coast Eagles": "win",
        "Basketball Match": "loss",
        "Rugby Match": "win",
    }
    return simulated_outcomes.get(event_name, None)

# Serialize a bet object into a dictionary
def serialize_bet(bet):
    return {
        "event_name": bet.event_name,
        "bet_type": bet.bet_type,
        "stake_amount": bet.stake_amount,
        "odds": bet.odds,
        "potential_winnings": bet.potential_winnings,
        "scheduled_time": bet.scheduled_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "duration": bet.duration,
        "status": bet.status,
        "actual_winnings": bet.actual_winnings,
        "date_settled": bet.date_settled.strftime("%Y-%m-%d %H:%M:%S") if bet.date_settled else None
    }

# Background task to update bet statuses and check outcomes
@app.before_request
def update_bet_statuses():
    if session.get('logged_in'):
        current_time = datetime.now()
        bets = PlacedBets.query.filter(PlacedBets.status.in_(["upcoming", "ongoing"])).all()

        for bet in bets:
            if bet.status == "upcoming" and bet.scheduled_time <= current_time:
                bet.status = "ongoing"
            elif bet.status == "ongoing" and bet.scheduled_time + bet.duration <= current_time:
                # Check event outcome
                event_result = EventResult.query.filter_by(event_name=bet.event_name).first()
                if not event_result:
                    outcome = fetch_event_outcome(bet.event_name)
                    if outcome:
                        event_result = EventResult(event_name=bet.event_name, outcome=outcome)
                        db.session.add(event_result)
                        db.session.commit()

                # Update bet based on outcome
                if event_result:
                    bet.event_outcome = event_result.outcome
                    bet.actual_winnings = bet.stake_amount * bet.odds if event_result.outcome == bet.bet_type else 0
                    bet.status = "past"
                    bet.date_settled = current_time

        db.session.commit() 

# Route for the global home page
@app.route("/")
def global_home():
    user_count = User.query.count()
    total_bets = PlacedBets.query.count()
    total_wins = sum(PlacedBets.query.filter(PlacedBets.actual_winnings > 0))
    biggest_win = PlacedBets.query.order_by(PlacedBets.actual_winnings.desc()).first()

    if isinstance(biggest_win, int):
        biggest_win = biggest_win  # Already an int, no change needed
    else:
        biggest_win = "N/A"

    return render_template("global_home.html", 
                           users=user_count,
                           total_bets=total_bets,
                           total_wins=total_wins,
                           biggest_win=biggest_win,
                           )  # Global home page

# Route for the dashboard
@app.route("/dashboard")
def dashboard():
    if not session.get('logged_in'):
        flash("You must be logged in to view the dashboard.", "error")
        return redirect(url_for('login'))

    # Fetch bets for the logged-in user
    user_id = session['userID']
    
    # Print debug info to check user_id
    print(f"Dashboard: Fetching bets for user_id: {user_id}")
    
    # Query all statuses separately with debugging
    ongoing_bets = PlacedBets.query.filter_by(user_id=user_id, status="ongoing").all()
    print(f"Ongoing bets found: {len(ongoing_bets)}")
    
    upcoming_bets = PlacedBets.query.filter_by(user_id=user_id, status="upcoming").all()
    print(f"Upcoming bets found: {len(upcoming_bets)}")
    for bet in upcoming_bets:
        print(f"  - Upcoming bet: {bet.event_name}, {bet.bet_type}, {bet.stake_amount}")
    
    past_bets = PlacedBets.query.filter_by(user_id=user_id, status="past").order_by(PlacedBets.date_settled.desc()).all()
    print(f"Past bets found: {len(past_bets)}")
    
    last_5_past_bets = past_bets[:5]
    created_bets = CreatedBets.query.filter_by(created_by=user_id).all()
    print(f"Created bets found: {len(created_bets)}")

    # Force the session to refresh data from the database
    db.session.expire_all()
    
    return render_template(
        "dashboard.html",
        ongoing_bets=ongoing_bets,
        upcoming_bets=upcoming_bets,
        past_bets=past_bets,
        last_5_past_bets=last_5_past_bets,
        created_bets=created_bets
    )

@app.route('/dashboard/data')
def dashboard_data():
    if not session.get('logged_in'):
        return jsonify({"error": "User not logged in"}), 401

    user_id = session.get('userID')
    if not user_id:
        return jsonify({"error": "User ID not found in session"}), 401

    # Fetch bets for the logged-in user
    ongoing_bets = [serialize_bet(bet) for bet in PlacedBets.query.filter_by(user_id=user_id, status="ongoing").all()]
    upcoming_bets = [serialize_bet(bet) for bet in PlacedBets.query.filter_by(user_id=user_id, status="upcoming").all()]
    past_bets = [serialize_bet(bet) for bet in PlacedBets.query.filter_by(user_id=user_id, status="past").all()]
    created_bets = [serialize_bet(bet) for bet in CreatedBets.query.filter_by(created_by=user_id).all()]

    return jsonify({
        "ongoing_bets": ongoing_bets,
        "upcoming_bets": upcoming_bets,
        "past_bets": past_bets,
        "created_bets": created_bets
    })

# Route for the "Create Bet" page (GET and POST methods)
@app.route('/create_bet', methods=['GET', 'POST'])
def create_bet():   
    if not session.get('logged_in'):
        flash("You must be logged in to create a bet.", "error")
        return redirect(url_for('login'))

    form = CreateBetForm()
    if form.validate_on_submit():
        # Convert duration in hours to timedelta
        duration = timedelta(hours=form.duration.data)

        # Ensure scheduled_time is in the future
        if form.scheduled_time.data <= datetime.now():
            flash("Scheduled time must be in the future.", "error")
            return render_template("create_bet.html", form=form)

        # Create a new bet
        new_created_bet = CreatedBets(
            event_name=form.event_name.data,
            bet_type=form.bet_type.data,
            max_stake=form.max_stake.data,
            odds=form.odds.data,
            scheduled_time=form.scheduled_time.data,
            duration=duration, 
            created_by=session['userID']
        )
        new_active_bet = ActiveBets(
            event_name=form.event_name.data,
            bet_type=form.bet_type.data,
            max_stake=form.max_stake.data,
            odds=form.odds.data,
            scheduled_time=form.scheduled_time.data,
            duration=duration, 
            created_by=session['userID']
        )
        try:
            print(f"Creating new_active_bet: {new_active_bet}")  # Debugging
            db.session.add(new_created_bet)
            db.session.add(new_active_bet)
            db.session.commit()
            flash("Bet created successfully!", "success")
            return redirect(url_for('active_bets'))
        except Exception as e:
            db.session.rollback()
            print(f"Error while creating bet: {str(e)}")  # Debugging
            flash(f"An error occurred: {str(e)}", "error")
    
    return render_template("create_bet.html", form=form)


# Route for active bets (all upcoming or ongoing bets)
@app.route("/active_bets")
def active_bets():
    current_time = datetime.now()
    print("Current time:", current_time)
    bets = ActiveBets.query.filter(
        ActiveBets.scheduled_time > current_time
    ).all()
    form = PlaceBetForm()
    return render_template("active_bets.html", bets=bets, form=form)


# Route for placing a bet
@app.route("/place_bet/<int:bet_id>", methods=["POST"])
def place_bet(bet_id):
    if not session.get('logged_in'):
        flash("You must be logged in to place a bet.", "error")
        return redirect(url_for('login'))

    form = PlaceBetForm()
    if form.validate_on_submit():
        amount = form.stake_amount.data
        user_currency = session['currency']

        if amount > user_currency:
            flash("Insufficient funds to place this bet.", "error")
            return redirect(url_for('active_bets'))

        # Retrieve the bet from the ActiveBets table
        bet = ActiveBets.query.get(bet_id)
        if not bet: 
            flash("Bet not found.", "error")
            return redirect(url_for('dashboard')) 

        # Ensure the user is not betting on their own event
        if bet.created_by == session['userID']:
            flash("You cannot place a bet on your own event.", "error")
            return redirect(url_for('active_bets'))

        # Add the bet to the PlacedBets table
        new_placed_bet = PlacedBets(
            user_id=session['userID'],
            event_name=bet.event_name,
            bet_type=bet.bet_type,
            stake_amount=amount,
            odds=bet.odds,
            potential_winnings=float(amount) * float(bet.odds),
            scheduled_time=bet.scheduled_time,
            duration=bet.duration,
            status="upcoming"  # Default status
        )
        
        try:
            user_id = session['userID']
            user = User.query.get(user_id)
            new_currency = float(user.currency) - float(amount)
            session['currency'] = new_currency

            db.session.add(new_placed_bet)
            db.session.commit()
    
            # Verify the bet was added by querying it back
            added_bet = PlacedBets.query.filter_by(
                user_id=session['userID'], 
                event_name=bet.event_name,
                bet_type=bet.bet_type
            ).order_by(PlacedBets.id.desc()).first()
             
            
            flash("Bet placed successfully!", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback() 
            flash(f"An error occurred: {str(e)}", "error") 

    return redirect(url_for('active_bets'))



@app.route("/forum")
def forum():
    # Get distinct categories from the database for the filter
    filter_categories = db.session.query(Post.category).distinct().all()
    filter_categories = [category[0] for category in filter_categories]  # Unwrap tuple

    # Get the selected category from the request args (default to 'all')
    selected_category = request.args.get('category', 'all')

    # Query posts based on the selected category
    if selected_category == 'all':
        filtered_posts = Post.query.order_by(Post.timestamp.desc()).all()
    else:
        filtered_posts = Post.query.filter_by(category=selected_category).order_by(Post.timestamp.desc()).all()

    # Render the forum page with posts and categories
    return render_template("forum.html", posts=filtered_posts, filter_categories=filter_categories, category=selected_category)

'''@app.route("/games") 
def game_board():
    return render_template("game_board.html")'''

# Route for the sign-up page (GET method)
@app.route("/signup")
def signup():
    return render_template("signup.html")  # Sign-up page

# Route for the sign-up page (POST method)
@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    if not username or not password or not email:
        flash('Please fill in all fields', 'error')
        return render_template("signup.html")
    
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        flash("Username or email already taken", 'error')
        return render_template("signup.html")
    
    new_user = User(username=username, password=password, email=email, currency=100) #hash password for storing implement soontm
    try:
        db.session.add(new_user)
        db.session.commit()
        flash("User created successfully", 'success')
        return redirect(url_for('login'))
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", 'error')
        return render_template('signup.html')

    '''# Example validation; replace with actual database logic
    if username and password:
        # Save user to database (example logic)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Please fill in all fields"})'''

# Route for the login page (GET method)
@app.route("/login")
def login():
    return render_template("login.html")  # Login page

# Route for the login page (POST method)
@app.route('/login', methods=['POST'])
def login_post():
    identifier = request.form.get('username')  # Can be username or email
    password = request.form.get('password')

    user = User.query.filter(
        ((User.username == identifier) | (User.email == identifier)) & (User.password == password)
    ).first()

    if user:
        session['logged_in'] = True
        session['username'] = user.username
        session['userID'] = user.id
        session['currency'] = user.currency
        return redirect(url_for('global_home'))
    else:
        flash("Login failed", 'error')
        return render_template('login.html')

    '''# Example validation; replace with actual database logic
    if username == "testuser" and password == "password123":
        session['logged_in'] = True
        return redirect(url_for('global_home')) #jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"})'''

# Route for logging out
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('global_home'))

# Route for the stats API
@app.route('/api/stats')
def stats():
    # Replace with actual database queries
    stats_data = {
        "totalUsers": 1200,  # Example: Query the total number of users
        "totalBets": 5000,  # Example: Query the total number of bets placed
        "totalWins": 3200,  # Example: Query the total number of wins
        "biggestWin": 50000  # Example: Query the biggest win amount
    }
    return jsonify(stats_data)

@app.route("/profile")
def profile():
    #Example user account for development purposes
    user = {
        "username": "testuser",
        "email": "testuser@example.com",
        "stats": {
            "totalBets": 42,
            "wins": 30,
            "losses": 12,
            "biggestWin": 5000
        },
        "date_joined" : "2023-01-01",
        "bets": [
            {"bet_id": 1, "game": "Poker", "amount": 100, "outcome": "Loss", "date": "2023-01-15"},
            {"bet_id": 2, "game": "Horses", "amount": 300, "outcome": "Won", "date": "2023-01-17"},
        ]
    }
    return render_template("profile.html", user=user)

@app.route("/createpost", methods=['GET', 'POST'])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            body=form.post.data, 
            category=form.category.data, 
            timestamp = datetime.now().replace(second=0, microsecond=0), 
            author=session['username'], 
            title=form.title.data
        )  # Example author ID
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('view_post', post_id=post.id))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template("forum_create_post.html", title='Create Post', form=form, posts=posts)

@app.route('/posts/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = Post.query.get(post_id)
    form = ReplyForm()
    if form.validate_on_submit():
        reply = Reply(
            body = form.reply.data, 
            timestamp = datetime.now().replace(second=0, microsecond=0), 
            author = form.author.data, 
            post_id=post_id
        )  # Example author ID
        db.session.add(reply)
        db.session.commit()
        return redirect(url_for('view_post', post_id=post.id))
    return render_template('forum_post.html', post=post, replies=post.replies, form=form) 



# Route for the currency page
@app.route("/currency")
def currency():
    if session['logged_in']:
        return render_template("currency.html")  # Currency page

# Route for getting currency
@app.route("/get_currency", methods=['POST'])
def get_currency():
    if session['logged_in']:
        content = request.get_json()
        amount = int(content.get('amount', 0))
        user = User.query.filter((User.username == session['username']) & (User.id == session['userID'])).first()
        session['currency'] = user.currency + amount
        user.currency += amount
        db.session.commit()

        return jsonify({"success": True, "amount": amount, "new_balance": user.currency})

@app.template_filter('pretty_currency')
def pretty_currency(cents):
    return "{:,}".format(int(cents))

if __name__ == "__main__":
    app.run(debug=True)
