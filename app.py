import os
import requests
import datetime
import random
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sentinel_recruiter_access_2026')

# --- 1. CLOUD DATABASE CONFIG ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sentinel_ultra.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MachineLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.String(50))
    temperature = db.Column(db.Float)
    vibration = db.Column(db.Float)
    status = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

with app.app_context():
    db.create_all()

# --- 2. TELEGRAM CONFIG (From Render Dashboard) ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PENDING_OTP = {}

def send_telegram_msg(text):
    if not TOKEN or not CHAT_ID: return False
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text})
        return r.status_code == 200
    except: return False

# --- 3. AUTHENTICATION (With Guest Access) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        
        # GUEST ACCESS: For Recruiters to enter instantly
        if user == "guest":
            session['logged_in'] = True
            session['user_type'] = "Guest"
            return redirect(url_for('index'))
            
        # ADMIN ACCESS: For your professional demo with 2FA
        if user == "Pravallika" and pw == "Princy@2115":
            otp = str(random.randint(100000, 999999))
            PENDING_OTP['current'] = otp
            send_telegram_msg(f"🔐 SENTINEL CLOUD ACCESS\nOTP: {otp}")
            return redirect(url_for('verify_page'))
            
        return render_template('login.html', error="Invalid Credentials. Try 'guest' to explore.")
    return render_template('login.html')

@app.route('/verify')
def verify_page(): return render_template('verify_otp.html')

@app.route('/verify_logic', methods=['POST'])
def verify_logic():
    if request.form.get('otp') == PENDING_OTP.get('current'):
        session['logged_in'] = True
        session['user_type'] = "Admin"
        return redirect(url_for('index'))
    return "Invalid OTP", 401

# --- 4. DATA & REPORTING ROUTES ---

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

@app.route('/export_report/<m_id>')
def export_report(m_id):
    logs = MachineLog.query.filter_by(machine_id=m_id).limit(50).all()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, f"INDUSTRIAL AUDIT: {m_id}", 1, 1, 'C')
    pdf.ln(10)
    for l in logs:
        pdf.cell(190, 8, f"{l.timestamp} | {l.temperature}C | {l.status}", 0, 1)
    path = f"/tmp/{m_id}_audit.pdf"
    pdf.output(path)
    return send_file(path, as_attachment=True)

@app.route('/ingest', methods=['POST'])
def ingest():
    data = request.json
    m_id, temp, vib = data.get("machine_id"), data.get("temperature"), data.get("vibration", 0.5)
    mode = "EMERGENCY" if temp > 85 or vib > 0.9 else ("WARNING" if temp > 75 or vib > 0.7 else "NORMAL")
    new_entry = MachineLog(machine_id=m_id, temperature=temp, vibration=vib, status=mode)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"status": "received"}), 201

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()