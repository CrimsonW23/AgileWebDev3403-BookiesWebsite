from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import PostForm, ReplyForm
from datetime import datetime, timedelta
from dashboard_handler import handle_dashboard, handle_dashboard_data
from bet_handler import handle_create_bet, handle_place_bet, handle_place_bet_form

import os

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = '9f8c1e6e49b4d9e6b2c442a1a8f3ecb1' #Session id used for testing

from extensions import db

db.init_app(app)
migrate = Migrate(app, db)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

from proj_models import User, Post, Reply, Bet, EventResult, ActiveBets

# Route for the global home page
@app.route("/")
def global_home():
    user_count = User.query.count()
    total_bets = Bet.query.count()
    total_wins = sum(Bet.query.filter(Bet.actual_winnings > 0))
    biggest_win = Bet.query.order_by(Bet.actual_winnings.desc()).first()

    if isinstance(biggest_win, int):
        biggest_win = biggest_win  # Already an int, no change needed
    else:
        biggest_win = "N/A"

    return render_template("global_home.html", 
                           users = user_count,
                           total_bets = total_bets,
                           total_wins = total_wins,
                           biggest_win = biggest_win,
                           )  # Global home page

# Route for the dashboard
@app.route("/dashboard")
def dashboard():
    if session['logged_in']:
        return handle_dashboard()

@app.route("/dashboard_data")
def dashboard_data():
    if session['logged_in']:
        return handle_dashboard_data()

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

# Route for the "Create Bet" page (GET and POST methods)
@app.route('/create_bet', methods=['GET', 'POST'])
def create_bet():
    return handle_create_bet()

@app.route("/active_bets")
def active_bets():
    bets = ActiveBets.query.all()
    return render_template("active_bets.html", bets=bets)

# Route for placing a bet
@app.route("/place_bet/<int:bet_id>", methods=["POST"])
def place_bet(bet_id):
    amount = float(request.form.get('amount'))
    if amount <= session['currency']:
        userid = session['userID']
        return handle_place_bet(bet_id, amount, userid)

# Route for the "Place Bet Form" page
@app.route("/place_bet_form/<event_name>", methods=["GET", "POST"])
def place_bet_form(event_name):
    return handle_place_bet_form(event_name)

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
