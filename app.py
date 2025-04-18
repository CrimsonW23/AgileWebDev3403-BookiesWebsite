from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Route for the global home page
@app.route("/")
def global_home():
    return render_template("global_home.html")  # Global home page

# Route for the dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("index.html")  # Dashboard page

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
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"})

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

if __name__ == "__main__":
    app.run(debug=True)

