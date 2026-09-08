import os, requests, datetime, random
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF

app = Flask(__name__)
# Use a default secret key if the environment variable isn't set
app.secret_key = os.environ.get('SECRET_KEY', 'sentinel_production_key_2026')

# --- 1. CLOUD DB CONFIG ---
# This ensures the database is created in the correct folder on Render
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sentinel_cloud.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MachineLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.String(50))
    temperature = db.Column(db.Float)
    vibration = db.Column(db.Float)
    status = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

# --- 2. CONFIG FROM RENDER ENVIRONMENT ---
TOKEN = os.environ.get("8919728098:AAH71DEsykt2KhzQe_nkZD8z8lKxwqMAMcA")
CHAT_ID = os.environ.get("7201797239")

# --- 3. ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == "Pravallika" and request.form.get('password') == "Princy@2115":
            session['logged_in'] = True
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/')
def index():
    if not session.get('logged_in'): return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/get_machines')
def get_machines():
    machines = db.session.query(MachineLog.machine_id).distinct().all()
    return jsonify([m[0] for m in machines])

@app.route('/get_data/<m_id>')
def get_data(m_id):
    logs = MachineLog.query.filter_by(machine_id=m_id).order_by(MachineLog.id.desc()).limit(20).all()
    return jsonify([{"time": l.timestamp.strftime("%H:%M:%S"), "temp": l.temperature, "vib": l.vibration, "status": l.status} for l in reversed(logs)])

@app.route('/ingest', methods=['POST'])
def ingest():
    data = request.json
    m_id, temp, vib = data.get("machine_id"), data.get("temperature"), data.get("vibration", 0.5)
    mode = "EMERGENCY" if temp > 85 or vib > 0.9 else ("WARNING" if temp > 75 or vib > 0.7 else "NORMAL")
    
    with app.app_context():
        new_entry = MachineLog(machine_id=m_id, temperature=temp, vibration=vib, status=mode)
        db.session.add(new_entry)
        db.session.commit()
    return jsonify({"status": "ok"}), 201

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()