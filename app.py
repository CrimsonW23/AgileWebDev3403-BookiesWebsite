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

from proj_models import User, Post, Reply, Bet, EventResult

# Route for the global home page
@app.route("/")
def global_home():
    return render_template("global_home.html")  # Global home page

# Route for the dashboard
@app.route("/dashboard")
def dashboard():
    return handle_dashboard()

@app.route("/dashboard_data")
def dashboard_data():
    return handle_dashboard_data()

# Route for the forum
@app.route("/forum")
def forum():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template("forum.html", posts=posts)  # Forum page

@app.route("/games") 
def game_board():
    return render_template("game_board.html")

# Route for the sign-up page (GET method)
@app.route("/signup")
def signup():
    return render_template("signup.html")  # Sign-up page

# Route for the sign-up page (POST method)
@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    password = request.form.get('password')

    # Example validation; replace with actual database logic
    if username and password:
        # Save user to database (example logic)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Please fill in all fields"})

# Route for the login page (GET method)
@app.route("/login")
def login():
    return render_template("login.html")  # Login page

# Route for the login page (POST method)
@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    # Example validation; replace with actual database logic
    if username == "testuser" and password == "password123":
        session['logged_in'] = True
        return redirect(url_for('global_home')) #jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"})

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
            author=form.author.data, 
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

@app.route("/available_bets")
def available_bets():
    user_id = 1  # Replace with the logged-in user's ID

    # Fetch all events that the logged-in user has NOT placed a bet on
    available_events = Bet.query.filter(
        Bet.user_id != user_id,  # Exclude bets placed by the logged-in user
        Bet.status != "Completed"  # Exclude completed bets
    ).distinct(Bet.event_name).all()

    return render_template("available_bets.html", events=available_events)

# Route for the "Create Bet" page (GET and POST methods)
@app.route('/create_bet', methods=['GET', 'POST'])
def create_bet():
    return handle_create_bet()

# Route for placing a bet
@app.route("/place_bet/<int:bet_id>", methods=["POST"])
def place_bet(bet_id):
    return handle_place_bet(bet_id)

# Route for the "Place Bet Form" page
@app.route("/place_bet_form/<event_name>", methods=["GET", "POST"])
def place_bet_form(event_name):
    return handle_place_bet_form(event_name)

if __name__ == "__main__":
    app.run(debug=True)

