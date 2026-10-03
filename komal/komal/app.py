from flask import Flask, render_template, jsonify
from database import init_db
from scheduler import run_allocation
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/allocate', methods=['GET'])
def allocate():
    steps, schedule = run_allocation()
    return jsonify({
        "steps": steps,
        "schedule": schedule
    })

if __name__ == '__main__':
    if not os.path.exists("exam_system.db"):
        init_db()
    app.run(debug=True, port=5000)