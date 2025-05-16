from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, abort
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import PostForm, ReplyForm, CreateBetForm, PlaceBetForm, SignupForm, LoginForm, EditBetForm
from datetime import datetime, timedelta, date
from extensions import db
from proj_models import User, Post, Reply, CreatedBets, ActiveBets, PlacedBets, EventResult, Friendship, FriendRequest
from sqlalchemy import func, or_, and_
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

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

def init_friends_tables():
    with app.app_context():
        engine = db.get_engine(bind="friends")  # get the engine for the 'friends' bind
        FriendRequest.metadata.create_all(bind=engine)
        Friendship.metadata.create_all(bind=engine)

init_friends_tables()

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

def convert_timedelta(value):
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, timedelta):
        return value.total_seconds() / 3600
    raise ValueError(f"Cannot convert {type(value)} to hours")

# Serialize a bet object into a dictionary
def serialize_bet(bet):
    serialized = {
        "bet_id": bet.id,
        "event_name": bet.event_name,
        "bet_type_description": bet.bet_type_description,
        "bet_type": bet.bet_type,
        "odds": bet.odds,
        "scheduled_time": bet.scheduled_time.strftime("%Y-%m-%dT%H:%M:%S") if bet.scheduled_time else None,
        "duration": (bet.duration.total_seconds() / 3600) if isinstance(bet.duration, timedelta) else bet.duration,
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

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.post("/upload_avatar")
@login_required
def upload_avatar():
    file = request.files.get("avatar")
    if not file or file.filename == "":
#        flash("No file selected.", "error")
       return redirect(url_for("profile"))

    if not allowed_file(file.filename):
#        flash("Invalid file type.", "error")
        return redirect(url_for("profile"))

    filename  = secure_filename(f"{current_user.id}_{file.filename}")
    save_path = os.path.join(app.root_path, app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    # update DB
    current_user.profile_pic = filename
    db.session.commit()

#    flash("Profile picture updated!", "success")
    return redirect(url_for("profile"))

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
    current_date = datetime.now()

    # Fetch updated bets
    ongoing_bets = PlacedBets.query.filter_by(user_id=user_id, status="ongoing").all()
    upcoming_bets = db.session.query(PlacedBets, ActiveBets.max_stake).join(ActiveBets, PlacedBets.game_id == ActiveBets.id).filter(       PlacedBets.user_id == current_user.id,
        ActiveBets.scheduled_time > current_date
    ).all()
    past_bets = PlacedBets.query.filter_by(user_id=user_id, status="past").order_by(PlacedBets.date_settled.desc()).all()
    created_bets = CreatedBets.query.filter_by(created_by=user_id).all()

    

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
    
    form = EditBetForm()

    # Pass all data to the template
    return render_template(
        "dashboard.html",
        ongoing_bets=ongoing_bets,
        upcoming_bets=upcoming_bets,
        past_bets=past_bets,
        last_5_past_bets=past_bets[:5] if past_bets else [],
        created_bets=created_bets,
        chart_data=chart_data,
        form=form
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
        #upcoming_bets = [serialize_bet(bet) for bet in PlacedBets.query.filter_by(user_id=current_user.id, status="upcoming").all()]
        past_bets = [serialize_bet(bet) for bet in PlacedBets.query.filter_by(user_id=current_user.id, status="past").all()]
        created_bets = [serialize_bet(bet) for bet in CreatedBets.query.filter_by(created_by=current_user.id).all()]

        # Query PlacedBets + join ActiveBets to get max_stake
        bets_with_max_stake = (
            db.session.query(PlacedBets, ActiveBets.max_stake)
            .join(ActiveBets, PlacedBets.game_id == ActiveBets.id)  # Join condition
            .filter(
                PlacedBets.user_id == current_user.id,
                PlacedBets.status == "upcoming"
            )
            .all()
        )

        # Convert each result into a dict (including max_stake)
        result = []
        for placed_bet, max_stake in bets_with_max_stake:
            bet_dict = {
                **{k: v for k, v in placed_bet.__dict__.items() 
                if not k.startswith('_')},  # Filter out SQLAlchemy internals
                "max_stake": max_stake,
                "duration": convert_timedelta(placed_bet.duration)  # Convert timedelta to hours
            }
            result.append(bet_dict)

        return jsonify({
            "ongoing_bets": ongoing_bets,
            "upcoming_bets": result,
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
    already_bet = []
    if current_user.is_authenticated:
        already_bet = [bet.game_id for bet in PlacedBets.query.filter_by(user_id=current_user.id).all()]
    form = PlaceBetForm()
    return render_template("active_bets.html", bets=bets, form=form, betted=already_bet)


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
        
        # Check against max bet
        if amount > bet.max_stake:
            flash(f'Stake cannot exceed ${bet.max_stake}', 'error')
            return redirect(url_for('active_bets'))

        # Add the bet to the PlacedBets table
        new_placed_bet = PlacedBets(
            user_id=current_user.id,  # Use current_user.id
            game_id=bet_id,
            event_name=bet.event_name,
            bet_type_description=bet.bet_type_description,
            bet_type=bet.bet_type,
            stake_amount=amount,
            odds=bet.odds,
            potential_winnings=round(float(amount) * float(bet.odds),2),
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

@app.route('/get_bet_data/<int:bet_id>')
@login_required
def get_bet_data(bet_id):
    bet = PlacedBets.query.get_or_404(bet_id)
    if bet.user_id != current_user.id:
        abort(403)
    return jsonify({
        'stake_amount': bet.stake_amount,
        # Add other fields
    })

@app.route('/dashboard/check_currency', methods=['POST'])
@login_required
def check_currency():
    data = request.get_json()
    bet_id = data.get('bet_id')
    new_stake = float(data.get('new_stake'))
    
    # Get current bet stake
    bet = PlacedBets.query.get(bet_id)
    if bet.user_id != current_user.id:
        abort(403)
    
    # Calculate currency difference
    stake_diff = new_stake - bet.stake_amount
    
    # Check if user has enough currency
    enough_currency = current_user.currency >= stake_diff
    
    return jsonify({
        'enough_currency': enough_currency,
        'current_currency': current_user.currency,
        'required_diff': stake_diff
    })

@app.route('/dashboard/update_bet', methods=['POST'])
@login_required
def update_bet():
    data = request.get_json()
    bet_id = data.get('bet_id')
    new_stake = float(data.get('new_stake'))
    
    try:
        # Get the bet
        bet = PlacedBets.query.get_or_404(bet_id)
        if bet.user_id != current_user.id:
            abort(403)
        
        # Calculate currency difference
        stake_diff = new_stake - bet.stake_amount
        
        # Update user currency
        current_user.currency -= stake_diff
        
        # Update bet
        bet.stake_amount = new_stake
        bet.potential_winnings = round(new_stake * bet.odds,2)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_currency': current_user.currency,
            'new_stake': new_stake,
            'new_potential_winnings': bet.potential_winnings
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route("/forum")
@login_required
def forum():
    # Get the selected category from request args, default to 'all'
    selected_category = request.args.get('category', 'all')
    page = request.args.get('page', 1, type=int)
    posts_per_page = 10  # Number of posts per page

    # Get friend IDs list
    friend_ids = [friend.id for friend in current_user.friends()]

    # Build privacy filter based on whether user has friends
    if friend_ids:
        privacy_filter = or_(
            Post.privacy == 'public',
            and_(Post.privacy == 'friends', Post.author_id.in_(friend_ids)),
            Post.author_id == current_user.id
        )
    else:
        privacy_filter = or_(
            Post.privacy == 'public',
            Post.author_id == current_user.id
        )

    # Start query with privacy filter
    query = Post.query.filter(privacy_filter)

    # Filter by category if selected_category is not 'all'
    if selected_category != 'all':
        query = query.filter(Post.category == selected_category)

    # Order posts by newest first
    query = query.order_by(Post.timestamp.desc())

    # Paginate the results
    pagination = query.paginate(page=page, per_page=posts_per_page, error_out=False)
    posts = pagination.items

    # Fetch distinct categories for the filter dropdown
    filter_categories = db.session.query(Post.category).distinct().all()
    filter_categories = [cat[0] for cat in filter_categories]

    # Render the forum template
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

@app.post("/toggle_email_visibility")
@login_required
def toggle_email_visibility():
    # expects JSON: {"show": true/false}
    data = request.get_json()
    current_user.show_email = bool(data.get("show"))
    db.session.commit()
    return jsonify(success=True)

@app.post("/toggle_stats_visibility")
@login_required
def toggle_stats_visibility():
    current_user.show_stats = bool(request.get_json().get("show"))
    db.session.commit()
    return jsonify(success=True)

@app.post("/toggle_bets_visibility")
@login_required
def toggle_bets_visibility():
    current_user.show_bets = bool(request.get_json().get("show"))
    db.session.commit()
    return jsonify(success=True)


@app.route("/profile")
@app.route("/profile/<username>")
@login_required
def profile(username=None):
    # 1. Decide whose page we’re showing
    if username is None:
        # No slug → show the logged-in user's profile
        db_user = current_user
    else:
        # Slug present → look that person up (404 if not found)
        db_user = User.query.filter_by(username=username).first_or_404()

    past_bets_q = PlacedBets.query.filter_by(user_id=db_user.id, status="past")
    total_bets  = past_bets_q.count()
    wins_q      = past_bets_q.filter(PlacedBets.actual_winnings > 0)
    wins        = wins_q.count()
    biggest_win = wins_q.order_by(PlacedBets.actual_winnings.desc()).first()
    biggest_win = biggest_win.actual_winnings if biggest_win else 0
    win_rate    = round(wins / total_bets * 100, 2) if total_bets else 0

    # 2. Prepare dict for the template
    user_dict = {
        "id":            db_user.id,
        "username":      db_user.username,
        "email":         db_user.email,
        "show_email":    db_user.show_email,
        "date_joined":   db_user.date_joined.strftime("%Y-%m-%d"),
        "profile_pic":   db_user.profile_pic or "default.png",
        "show_stats":    db_user.show_stats,
        "show_bets":     db_user.show_bets,
        "stats": {
            "total":  total_bets,
            "wins":   wins,
            "biggest":biggest_win,
            "rate":   win_rate
        },
        "bets":          past_bets_q.order_by(PlacedBets.date_settled.desc()).all()
    }
    return render_template("profile.html", user=user_dict)

# --- Profile search -------------------------------------------------
@app.route("/search_profiles")
@login_required
def search_profiles():
    """
    Return a page of users whose username contains the query string (?q=...).
    """
    q = request.args.get("q", "").strip()

    # Basic search: case-insensitive LIKE on username
    results = []
    if q:
        results = User.query.filter(User.username.ilike(f"%{q}%")).all()

    return render_template(
        "search_results.html",
        query=q,
        users=results,
    )

# --- Friends page -------------------------------------------------
@app.route("/friends")
@login_required
def friends():
    # 1. Pull friend IDs from friends.db
    session_friends: Session = db.session
    session_friends.bind = db.get_engine(app, bind="friends")

    friend_ids = session_friends.scalars(
        db.select(Friendship.friend_id)
          .where(Friendship.user_id == current_user.id)
    ).all()

    # 2. Now pull the User rows from the main DB
    my_friends = User.query.filter(User.id.in_(friend_ids)).all() if friend_ids else []

    pending_in = session_friends.scalars(
        db.select(FriendRequest)
          .where((FriendRequest.to_id == current_user.id) &
                 (FriendRequest.status == "pending"))
    ).all()

    return render_template("friends.html",
                           friends=my_friends,
                           pending=pending_in)


@app.post("/friend-request/<username>")
@login_required
def send_friend_request(username):
    target = User.query.filter_by(username=username).first_or_404()

#    if current_user.id == target.id:
#        flash("That's you!", "info")
#    elif current_user.is_friends_with(target):
#        flash("Already friends.", "info")
#    elif current_user.has_pending_with(target):
#        flash("Request already pending.", "warning")
#    else:

    # Remove line below if above if-statements are uncommented
    if current_user.id != target.id and not current_user.is_friends_with(target) and not current_user.has_pending_with(target):
        fr = FriendRequest(from_id=current_user.id, to_id=target.id)
        db.session.add(fr)
        db.session.commit()
#        flash(f"Request sent to {target.username}.", "success")

    return redirect(request.referrer or url_for("search_profiles"))

@app.post("/friend-request/<int:rid>/accept")
@login_required
def accept_friend_request(rid):
    fr = FriendRequest.query.get_or_404(rid)

    # Use Flask-Login's current_user for access control
    if fr.to_id != current_user.id or fr.status != "pending":
#        flash("Cannot accept.", "error")
        return redirect(url_for("friends"))

    # Mark accepted & create reciprocal rows
    fr.status = "accepted"
    db.session.add_all([
        Friendship(user_id=fr.from_id, friend_id=fr.to_id),
        Friendship(user_id=fr.to_id,   friend_id=fr.from_id)
    ])
    db.session.commit()

#    flash("Friend request accepted.", "success")
    return redirect(url_for("friends"))

    
@app.route("/createpost", methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            body=form.post.data,
            category=form.category.data,
            timestamp=datetime.now().replace(second=0, microsecond=0),
            author_id=current_user.id,  
            title=form.title.data,
            privacy=form.privacy.data
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
            author_id=current_user.id,
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
