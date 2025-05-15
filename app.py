from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import PostForm, ReplyForm, CreateBetForm, PlaceBetForm, SignupForm, LoginForm
from datetime import datetime, timedelta, date
from extensions import db
from proj_models import User, Post, Reply, CreatedBets, ActiveBets, PlacedBets, EventResult
from sqlalchemy import func
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

import os

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#test data
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
    serialized = {
        "event_name": bet.event_name,
        "bet_type_description": bet.bet_type_description,
        "bet_type": bet.bet_type,
        "odds": bet.odds,
        "scheduled_time": bet.scheduled_time.strftime("%Y-%m-%dT%H:%M:%S") if bet.scheduled_time else None,
        "duration": bet.duration.total_seconds() if isinstance(bet.duration, timedelta) else bet.duration,
        "status": bet.status
    }

    # Add attributes specific to CreatedBets
    if hasattr(bet, 'max_stake'):
        serialized["max_stake"] = bet.max_stake

    # Add attributes specific to PlacedBets
    if hasattr(bet, 'stake_amount'):
        serialized["stake_amount"] = bet.stake_amount
    if hasattr(bet, 'potential_winnings'):
        serialized["potential_winnings"] = bet.potential_winnings
    if hasattr(bet, 'actual_winnings'):
        serialized["actual_winnings"] = bet.actual_winnings
    if hasattr(bet, 'date_settled'):
        serialized["date_settled"] = bet.date_settled.strftime("%Y-%m-%d %H:%M:%S") if bet.date_settled else None

    return serialized

# Background task to update bet statuses and check outcomes
@app.before_request
def update_bet_statuses():
    if current_user.is_authenticated:  
        current_time = datetime.now()
        
        # Update PlacedBets statuses
        placed_bets = PlacedBets.query.filter(PlacedBets.status.in_(["upcoming", "ongoing"])).all()
        
        for bet in placed_bets: 
            if isinstance(bet.duration, int):
                duration = timedelta(hours=bet.duration)
            else:
                duration = bet.duration
                
            end_time = bet.scheduled_time + duration
            
            if bet.status == "upcoming" and bet.scheduled_time <= current_time:
                bet.status = "ongoing"
            elif bet.status == "ongoing" and end_time <= current_time:
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
        
        # Update CreatedBets statuses
        created_bets = CreatedBets.query.filter(CreatedBets.status.in_(["upcoming", "ongoing"])).all()
        for bet in created_bets:
            if isinstance(bet.duration, int):
                duration = timedelta(hours=bet.duration)
            else:
                duration = bet.duration
                
            end_time = bet.scheduled_time + duration
            
            if bet.status == "upcoming" and bet.scheduled_time <= current_time:
                bet.status = "ongoing"
            elif bet.status == "ongoing" and end_time <= current_time:
                bet.status = "past"

        db.session.commit()

# Route for the global home page
@app.route("/")
def global_home():
    user_count = User.query.count()
    total_bets = PlacedBets.query.count()
    total_wins = db.session.query(func.sum(PlacedBets.actual_winnings)).filter(PlacedBets.actual_winnings > 0).scalar() or 0
    biggest_win = PlacedBets.query.order_by(PlacedBets.actual_winnings.desc()).first()

    if biggest_win and isinstance(biggest_win.actual_winnings, (int, float)):
        biggest_win = biggest_win.actual_winnings
    else:
        biggest_win = "N/A"

    return render_template(
        "global_home.html",
        users=user_count,
        total_bets=total_bets,
        total_wins=total_wins,
        biggest_win=biggest_win,
    )

# Route for the terms and conditions page
@app.route('/terms_conditions')
def terms_conditions():
    return render_template('terms_conditions.html')

# Route for the privacy policy page
@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')

# Route for the responsible gambling page
@app.route('/responsible_gambling')
def responsible_gambling():
    return render_template('responsible_gambling.html')

# Route for the sign-up page (GET and POST methods)
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    
    if form.validate_on_submit():
        # Extract form data
        username = form.username.data
        password = form.password.data
        email = form.email.data
        
        # Check if username or email already exists
        existing_user = User.query.filter((User.email == email) | (User.username == username) ).first()
        if existing_user:
            if existing_user.email == email:
                flash("The email is already registered. Please use a different email", 'error')
            if existing_user.username == username:
                flash("The username is already taken. Please choose a different one", 'error')
            return render_template("signup.html", form=form)
        
        # Create a new user
        try:
            new_user = User(
                username=username,
                email=email,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone=form.phone.data,
                country=form.country.data,
                dob=form.dob.data,
                currency=100  # Default currency value
            )
            new_user.set_password(password)  # Hash the password before storing
            
            db.session.add(new_user)
            db.session.commit()
            
            # Log the user in after signup
            login_user(new_user) 
            return redirect(url_for('global_home'))  
        
        except Exception as e:
            db.session.rollback() 
            return render_template("signup.html", form=form)
    
    # If form validation failed, handle errors without flashing
    elif request.method == 'POST':
        pass  
    
    return render_template("signup.html", form=form)
   
# Route for the login page (GET and POST methods)
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if request.method == 'GET':
        return render_template("login.html", form=form)
    
    if form.validate_on_submit():
        username = form.username.data.strip().lower()
        password = form.password.data

    user = User.query.filter(
        (func.lower(User.username) == username) | 
        (func.lower(User.email) == username)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({
            "success": False,
            "message": "Invalid Username/Email or Password"
        }) 
 
    db.session.commit()
    
    # Force session creation
    login_user(user, remember=True, force=True)

    return jsonify({
        "success": True,
        "redirect": url_for('global_home')
    })

# Route for logging out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('global_home'))

# Dashboard route
@app.route("/dashboard")
@login_required
def dashboard():
    update_bet_statuses()  # Call the function to update bet statuses

    user_id = current_user.id

    # Fetch updated bets
    ongoing_bets = PlacedBets.query.filter_by(user_id=user_id, status="ongoing").all()
    upcoming_bets = PlacedBets.query.filter_by(user_id=user_id, status="upcoming").all()
    past_bets = PlacedBets.query.filter_by(user_id=user_id, status="past").order_by(PlacedBets.date_settled.desc()).all()
    created_bets = CreatedBets.query.filter_by(created_by=user_id).all()

    # Fetch stats data for the charts
    current_date = datetime.now()

    # Helper function to calculate wins and losses
    def calculate_wins_and_losses(bets):
        wins = sum(1 for bet in bets if bet.actual_winnings > 0)
        losses = len(bets) - wins
        return wins, losses

    # Get monthly data for all months of the current year (for Pie Chart and Line Chart)
    months_data = []
    wins_data = []

    for month in range(1, 13):  # Loop through all months of the year
        month_start = datetime(current_date.year, month, 1)
        if month == 12:
            month_end = datetime(current_date.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            month_end = datetime(current_date.year, month + 1, 1) - timedelta(seconds=1)

        # Query bets for this month
        month_bets = PlacedBets.query.filter(
            PlacedBets.user_id == user_id,
            PlacedBets.status == "past",
            PlacedBets.date_settled >= month_start,
            PlacedBets.date_settled <= month_end
        ).all()

        # Count wins for the month
        wins_count, _ = calculate_wins_and_losses(month_bets)

        # Add to data arrays
        month_name = month_start.strftime("%b")
        months_data.append(month_name)
        wins_data.append(wins_count)

    # Calculate win/loss ratio for the most recent month (for Pie Chart)
    last_month_start = (current_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_month_end = current_date.replace(day=1) - timedelta(days=1)

    last_month_bets = PlacedBets.query.filter(
        PlacedBets.user_id == user_id,
        PlacedBets.status == "past",
        PlacedBets.date_settled >= last_month_start,
        PlacedBets.date_settled <= last_month_end
    ).all()

    wins_count, losses_count = calculate_wins_and_losses(last_month_bets)

    # Calculate overall net profit (for Net Profit Chart)
    if past_bets:
        overall_net_profit = sum(bet.actual_winnings - bet.stake_amount for bet in past_bets)
        is_net_profit_positive = overall_net_profit > 0
    else:
        overall_net_profit = None   
        is_net_profit_positive = None

    # Calculate overall win rate (for Win Rate Chart) 
    total_bets = len(past_bets)
    if total_bets > 0:
        total_wins = sum(1 for bet in past_bets if bet.actual_winnings > 0)
        overall_win_rate = (total_wins / total_bets) * 100
    else:
        total_wins = 0
        overall_win_rate = None   
        

    # Prepare chart data
    chart_data = {
        "net_profit": {
            "overall": overall_net_profit,
            "is_positive": is_net_profit_positive
        },
        "win_rate": {
            "wins": total_wins,
            "losses": total_bets - total_wins if total_bets > 0 else 0,
            "rate": overall_win_rate   
        },
        "monthly_wins": {
            "months": months_data,
            "wins": wins_data
        },
        "win_loss_ratio": {
            "wins": wins_count,
            "losses": losses_count
        }
    }

    # Pass all data to the template
    return render_template(
        "dashboard.html",
        ongoing_bets=ongoing_bets,
        upcoming_bets=upcoming_bets,
        past_bets=past_bets,
        last_5_past_bets=past_bets[:5] if past_bets else [],
        created_bets=created_bets,
        chart_data=chart_data
    )

@app.route('/dashboard/data')
@login_required
def dashboard_data():
    try:
        # Dynamically update bet statuses
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

        # Fetch updated bets for the logged-in user
        ongoing_bets = [serialize_bet(bet) for bet in PlacedBets.query.filter_by(user_id=current_user.id, status="ongoing").all()]
        upcoming_bets = [serialize_bet(bet) for bet in PlacedBets.query.filter_by(user_id=current_user.id, status="upcoming").all()]
        past_bets = [serialize_bet(bet) for bet in PlacedBets.query.filter_by(user_id=current_user.id, status="past").all()]
        created_bets = [serialize_bet(bet) for bet in CreatedBets.query.filter_by(created_by=current_user.id).all()]

        return jsonify({
            "ongoing_bets": ongoing_bets,
            "upcoming_bets": upcoming_bets,
            "past_bets": past_bets,
            "created_bets": created_bets
        })
    except Exception as e: 
        return jsonify({"error": str(e)})

# Route for the "Create Bet" page (GET and POST methods)
@app.route('/create_bet', methods=['GET', 'POST'])
@login_required
def create_bet():
    form = CreateBetForm()
    if form.validate_on_submit():
        # Convert duration in hours to timedelta
        duration = timedelta(hours=form.duration.data)

        # Ensure scheduled_time is in the future
        if form.scheduled_time.data <= datetime.now():
            return render_template("create_bet.html", form=form)

        # Create a new bet
        new_created_bet = CreatedBets(
            event_name=form.event_name.data,
            bet_type_description=form.bet_type_description.data,
            bet_type=form.bet_type.data,
            max_stake=form.max_stake.data,
            odds=form.odds.data,
            scheduled_time=form.scheduled_time.data,
            duration=duration,
            created_by=current_user.id  
        )
        new_active_bet = ActiveBets(
            event_name=form.event_name.data,
            bet_type_description=form.bet_type_description.data,
            bet_type=form.bet_type.data,
            max_stake=form.max_stake.data,
            odds=form.odds.data,
            scheduled_time=form.scheduled_time.data,
            duration=duration,
            created_by=current_user.id   
        )
        try:
            db.session.add(new_created_bet)
            db.session.add(new_active_bet)
            db.session.commit()
            return redirect(url_for('active_bets'))
        except Exception as e:
            db.session.rollback()

    return render_template("create_bet.html", form=form)


# Route for active bets page
@app.route("/active_bets")
def active_bets():
    current_time = datetime.now() 
    bets = ActiveBets.query.filter(
        ActiveBets.scheduled_time > current_time
    ).all()
    form = PlaceBetForm()
    return render_template("active_bets.html", bets=bets, form=form)


# Route for placing a bet
@app.route("/place_bet/<int:bet_id>", methods=["POST"])
@login_required
def place_bet(bet_id):
    form = PlaceBetForm()
    if form.validate_on_submit():
        amount = form.stake_amount.data
        user_currency = current_user.currency   

        if amount > user_currency:
            return redirect(url_for('active_bets'))

        # Retrieve the bet from the ActiveBets table
        bet = ActiveBets.query.get(bet_id)
        if not bet:
            return redirect(url_for('dashboard'))

        # Ensure the user is not betting on their own event
        if bet.created_by == current_user.id:  
            return redirect(url_for('active_bets'))

        # Add the bet to the PlacedBets table
        new_placed_bet = PlacedBets(
            user_id=current_user.id,  # Use current_user.id
            event_name=bet.event_name,
            bet_type_description=bet.bet_type_description,
            bet_type=bet.bet_type,
            stake_amount=amount,
            odds=bet.odds,
            potential_winnings=float(amount) * float(bet.odds),
            scheduled_time=bet.scheduled_time,
            duration=bet.duration,
            status="upcoming"  
        )

        try:
            # Deduct the stake amount from the user's currency
            current_user.currency -= float(amount)
            db.session.add(new_placed_bet)
            db.session.commit()
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()

    return redirect(url_for('active_bets'))


@app.route("/forum")
def forum():
    # Get distinct categories from the database for the filter
    filter_categories = db.session.query(Post.category).distinct().all()
    filter_categories = [category[0] for category in filter_categories]  # Unwrap tuple

    # Get the selected category from the request args (default to 'all')
    selected_category = request.args.get('category', 'all')

    # Pagination
    page = request.args.get('page', 1, type=int)
    posts_per_page = 10  # Number of posts per page

    # Query posts based on the selected category
    if selected_category == 'all':
        query = Post.query.order_by(Post.timestamp.desc())
    else:
        query = Post.query.filter_by(category=selected_category).order_by(Post.timestamp.desc())

    pagination = query.paginate(page=page, per_page=posts_per_page, error_out=False)
    posts = pagination.items

    # Render the forum page
    return render_template(
        "forum.html",
        posts=posts,
        pagination=pagination,
        category=selected_category,
        filter_categories=filter_categories
    )

'''@app.route("/games") 
def game_board():
    return render_template("game_board.html")'''

@app.route("/profile")
@login_required
def profile():
    user = {
        "username": current_user.username,
        "email": current_user.email,
        "stats": {
            "totalBets": PlacedBets.query.filter_by(user_id=current_user.id).count(),
            "wins": PlacedBets.query.filter_by(user_id=current_user.id, event_outcome="win").count(),
            "losses": PlacedBets.query.filter_by(user_id=current_user.id, event_outcome="loss").count(),
            "biggestWin": db.session.query(func.max(PlacedBets.actual_winnings)).filter_by(user_id=current_user.id).scalar() or 0
        },
        "date_joined": current_user.date_joined,
        "bets": PlacedBets.query.filter_by(user_id=current_user.id).order_by(PlacedBets.date_settled.desc()).limit(5).all()
    }
    return render_template("profile.html", user=user)

@app.route("/createpost", methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            body=form.post.data,
            category=form.category.data,
            timestamp=datetime.now().replace(second=0, microsecond=0),
            author=current_user.username,  
            title=form.title.data
        )
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
            body=form.reply.data,
            timestamp=datetime.now().replace(second=0, microsecond=0),
            author=current_user.username if current_user.is_authenticated else "Anonymous",  
            post_id=post_id
        )
        db.session.add(reply)
        db.session.commit()
        return redirect(url_for('view_post', post_id=post.id))
    replies = post.replies.order_by(Reply.timestamp.desc()).all()
    return render_template('forum_post.html', post=post, replies=replies, form=form, now=datetime.now()) 

# Route for the currency page
@app.route("/currency")
@login_required
def currency():
    return render_template("currency.html") 

# Route for getting currency
@app.route("/get_currency", methods=['POST'])
@login_required
def get_currency():
    content = request.get_json()
    amount = int(content.get('amount', 0))
    current_user.currency += amount 
    db.session.commit()
    return jsonify({"success": True, "amount": amount, "new_balance": current_user.currency})

@app.template_filter('pretty_currency')
def pretty_currency(cents):
    return "{:,}".format(int(cents))
 
if __name__ == "__main__":
    app.run(debug=True)
