from flask import render_template, request, redirect, url_for, flash, session
from datetime import datetime
from proj_models import Bet, ActiveBets
from extensions import db

def handle_create_bet():
    """Handle the creation of a new bet."""
    if request.method == 'POST':
        try:
            # Collect and validate form data
            event_name = request.form.get("event-name")
            bet_type = request.form.get("bet-type")
            stake_amount = request.form.get("stake-amount")
            odds = request.form.get("odds")
            scheduled_time = request.form.get("scheduled-time")
            duration = request.form.get("duration")

            if not all([event_name, bet_type, stake_amount, odds, scheduled_time, duration]):
                flash("All fields are required.", "error")
                return redirect(url_for('create_bet'))

            scheduled_datetime = datetime.strptime(scheduled_time, "%Y-%m-%dT%H:%M")
            if scheduled_datetime <= datetime.now():
                flash("Scheduled time must be in the future.", "error")
                return redirect(url_for('create_bet'))

            # Save the bet to the ActiveBets table
            new_active_bet = ActiveBets(
                event_name=event_name,
                bet_type=bet_type,
                stake_amount=stake_amount,
                odds=odds,
                scheduled_time=scheduled_datetime,
                duration=int(duration),  # Save duration in hours 
            )
            db.session.add(new_active_bet)

            # Save the same bet to the Bet table
            new_bet = Bet(
                user_id=session['userID'],  # Use the logged-in user's ID
                event_name=event_name,
                bet_type=bet_type,
                stake_amount=float(stake_amount),
                odds=float(odds),
                potential_winnings=round(float(stake_amount) * float(odds), 2),
                scheduled_time=scheduled_datetime,
                duration=int(duration),  # Save duration in hours
                status="Upcoming"  # Default status
            )
            db.session.add(new_bet)

            # Commit both changes to the database
            db.session.commit()

            flash("Bet placed successfully!", "success")
            return redirect(url_for('active_bets'))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('create_bet'))

    # Render the form for GET requests
    return render_template('create_bet.html', current_time=datetime.now().strftime("%Y-%m-%dT%H:%M"))

def handle_place_bet(bet_id, amount): 

    user_id = session['userID']  # Get the logged-in user's ID

    # Fetch the original bet from the Bet table
    original_bet = Bet.query.get_or_404(bet_id)

    # Create a new bet for the user
    new_bet = Bet(
        user_id=user_id,  # Use the session's `userID`
        event_name=original_bet.event_name,
        bet_type=original_bet.bet_type,
        stake_amount=amount,
        odds=original_bet.odds,
        potential_winnings=round(amount * original_bet.odds, 2),
        scheduled_time=original_bet.scheduled_time,
        duration=original_bet.duration,
        status="Upcoming"  # Default status for the user's bet
    )
    db.session.add(new_bet)
    db.session.commit()

    flash("Bet placed successfully!", "success")
    return redirect(url_for("dashboard"))

def handle_place_bet_form(event_name):
    """Handle the form for placing a bet on an event."""
    original_event = Bet.query.filter_by(event_name=event_name).first()
    if not original_event:
        flash("Event not found.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        try:
            user_id = user_id
            bet_type = request.form.get("bet_type")
            stake_amount = float(request.form.get("stake_amount"))
            odds = float(request.form.get("odds"))

            if not bet_type or stake_amount < 1 or odds < 1:
                flash("Invalid input. Stake Amount and Odds must be greater than 1.", "error")
                return redirect(url_for("place_bet_form", event_name=event_name))

            # Create a new bet for the user
            new_bet = Bet(
                user_id = session['userID'],
                event_name=event_name,
                bet_type=bet_type,
                stake_amount=stake_amount,
                odds=odds,
                potential_winnings=stake_amount * odds,
                scheduled_time=original_event.scheduled_time,
                duration=original_event.duration,
                status="Upcoming"
            )
            db.session.add(new_bet)
            db.session.commit()

            flash("Bet placed successfully!", "success")
            return redirect(url_for("dashboard", _anchor="available"))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("place_bet_form", event_name=event_name))

    # Render the form for GET requests
    return render_template("place_bet_form.html", event_name=event_name)