from flask import render_template, jsonify
from datetime import datetime, timedelta
from proj_models import Bet, EventResult
from extensions import db

def fetch_event_outcome(event_name):
    """Simulate fetching the event outcome."""
    simulated_outcomes = {
        "Real Madrid vs Barcelona (Real Madrid Wins)": "win",
        "FIFA World Cup Final - (Team A Losses)": "loss",
        "AFL: Fremantle vs. West Coast Eagles (Fremantle Wins)": "win",
        "AFL: Fremantle vs. West Coast Eagles (West Coast Eagles Wins)": "win",
        "Real Madrid vs Barcelona (Barcelona Wins)": "loss",
        "FIFA World Cup Final - (Team B Wins)": "win",
        "Test 1": "win",
        "Test 2": "loss",
        "Football Match": "loss",
        "Basketball Match": "win",
        "Rugby Match": "win",
    }
    return simulated_outcomes.get(event_name)

def serialize_bet(bet):
    """Serialize a bet object into a dictionary."""
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

def update_bet_statuses(user_id):
    """Update the statuses of bets dynamically."""
    current_time = datetime.now()
    bets = Bet.query.filter_by(user_id=user_id).all()

    for bet in bets:
        duration = timedelta(hours=bet.duration)
        if bet.status == "Upcoming" and bet.scheduled_time <= current_time:
            bet.status = "Ongoing"
        elif bet.status == "Ongoing" and current_time >= (bet.scheduled_time + duration):
            event_result = EventResult.query.filter_by(event_name=bet.event_name).first()
            if not event_result:
                outcome = fetch_event_outcome(bet.event_name)
                if outcome:
                    event_result = EventResult(event_name=bet.event_name, outcome=outcome)
                    db.session.add(event_result)
                    db.session.commit()

            if event_result:
                bet.event_outcome = event_result.outcome
                bet.actual_winnings = bet.stake_amount * bet.odds if event_result.outcome == bet.bet_type else 0
                bet.status = "Completed"
                bet.date_settled = current_time

    db.session.commit()

def handle_dashboard():
    """Render the dashboard with updated bet data."""
    user_id = 1  # Placeholder user ID
    update_bet_statuses(user_id)

    # Fetch bets by status
    ongoing_bets = Bet.query.filter_by(user_id=user_id, status="Ongoing").all()
    upcoming_bets = Bet.query.filter_by(user_id=user_id, status="Upcoming").all()
    past_bets = Bet.query.filter_by(user_id=user_id, status="Completed").order_by(Bet.date_settled.desc()).all()
    last_5_past_bets = past_bets[:5]

    # Prepare data for charts
    monthly_wins = [0] * 12
    win_loss_ratio = {"wins": 0, "losses": 0}
    for bet in past_bets:
        if bet.date_settled:
            month = bet.date_settled.month - 1
            if bet.actual_winnings > 0:
                monthly_wins[month] += 1
                win_loss_ratio["wins"] += 1
            else:
                win_loss_ratio["losses"] += 1

    available_bets = Bet.query.filter(
        Bet.user_id != user_id,
        Bet.status == "Upcoming",
        Bet.scheduled_time > datetime.now()
    ).all()

    return render_template(
        "dashboard.html",
        ongoing_bets=ongoing_bets,
        upcoming_bets=upcoming_bets,
        past_bets=past_bets,
        last_5_past_bets=last_5_past_bets,
        available_bets=available_bets,
        monthly_wins=monthly_wins,
        win_loss_ratio=win_loss_ratio
    )

def handle_dashboard_data():
    """Return dashboard data as JSON."""
    user_id = 1  # Placeholder user ID
    update_bet_statuses(user_id)  # Ensure bet statuses are updated dynamically

    # Fetch bets by status
    ongoing_bets = Bet.query.filter_by(user_id=user_id, status="Ongoing").all()
    upcoming_bets = Bet.query.filter_by(user_id=user_id, status="Upcoming").all()
    past_bets = Bet.query.filter_by(user_id=user_id, status="Completed").order_by(Bet.date_settled.desc()).all()

    return jsonify({
        "ongoing_bets": [serialize_bet(bet) for bet in ongoing_bets],
        "upcoming_bets": [serialize_bet(bet) for bet in upcoming_bets],
        "past_bets": [serialize_bet(bet) for bet in past_bets]
    })
