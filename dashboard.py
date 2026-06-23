# dashboard.py - Flask web dashboard for viewing attack data
from flask import Flask, render_template, jsonify
from database import init_db, get_all_attacks, get_stats

app = Flask(__name__)

@app.route("/")
def index():
    # serve the main dashboard page
    return render_template("index.html")

@app.route("/api/attacks")
def api_attacks():
    # return all attacks as JSON for the frontend to consume
    attacks = get_all_attacks()
    return jsonify(attacks)

@app.route("/api/stats")
def api_stats():
    # return summary stats as JSON
    stats = get_stats()
    return jsonify(stats)

if __name__ == "__main__":
    init_db()
    # only accessible locally not exposed to internet
    app.run(host="127.0.0.1", port=5000, debug=False)
