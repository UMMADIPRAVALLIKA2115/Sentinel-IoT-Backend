import os
import requests
import datetime
import random
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF

app = Flask(__name__)

# --- 1. CLOUD SECURITY CONFIG ---
app.secret_key = os.environ.get('SECRET_KEY', 'sentinel_ultra_secure_99')

# --- 2. CLOUD DATABASE CONFIG ---
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

# --- 3. TELEGRAM CONFIG (Pulls from Render Dashboard) ---
# IMPORTANT: These must be typed in the Render "Environment" tab!
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Global variable to store OTP temporarily (Cloud-safe method)
PENDING_OTP = {}

def send_telegram_msg(text):
    """Sends messages and logs results for cloud debugging"""
    if not TOKEN or not CHAT_ID:
        print(f"❌ CLOUD ERROR: Environment Variables missing! TOKEN:{bool(TOKEN)} ID:{bool(CHAT_ID)}")
        return False
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    
    try:
        r = requests.post(url, json=payload)
        print(f"☁️ Telegram API Call: {r.status_code} - {r.text}")
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        return False

# --- 4. AUTHENTICATION & 2FA ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        
        if user == "Pravallika" and pw == "Princy@2115":
            otp = str(random.randint(100000, 999999))
            PENDING_OTP['current'] = otp # Save to global storage
            
            # Send the OTP
            success = send_telegram_msg(f"🔐 SENTINEL CLOUD ACCESS\nYour Secure Code: {otp}")
            
            if success:
                return redirect(url_for('verify_page'))
            else:
                return "Failed to send OTP. Please check Render Environment Variables.", 500
                
        return render_template('login.html', error="Invalid Credentials")
    return render_template('login.html')

@app.route('/verify')
def verify_page():
    return render_template('verify_otp.html')

@app.route('/verify_logic', methods=['POST'])
def verify_logic():
    user_otp = request.form.get('otp')
    if user_otp == PENDING_OTP.get('current'):
        session['logged_in'] = True
        PENDING_OTP.pop('current', None)
        return redirect(url_for('index'))
    return "Invalid OTP. Access Denied.", 401

@app.route('/test_bot')
def test_bot():
    """Diagnostic route to verify keys work from the browser"""
    result = send_telegram_msg("🚀 Sentinel Cloud Link Successful!")
    return f"Test Sent! Status: {'Success' if result else 'Failed'}. Check Render logs for details."

# --- 5. DASHBOARD & DATA ROUTES ---

@app.route('/')
def index():
    if not session.get('logged_in'): return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/get_machines')
def get_machines():
    if not session.get('logged_in'): return jsonify([]), 401
    machines = db.session.query(MachineLog.machine_id).distinct().all()
    return jsonify([m[0] for m in machines])

@app.route('/get_data/<m_id>')
def get_data(m_id):
    if not session.get('logged_in'): return jsonify([]), 401
    logs = MachineLog.query.filter_by(machine_id=m_id).order_by(MachineLog.id.desc()).limit(20).all()
    return jsonify([{"time": l.timestamp.strftime("%H:%M:%S"), "temp": l.temperature, "vib": l.vibration, "status": l.status} for l in reversed(logs)])

@app.route('/ingest', methods=['POST'])
def ingest():
    data = request.json
    m_id, temp, vib = data.get("machine_id"), data.get("temperature"), data.get("vibration", 0.5)
    mode = "EMERGENCY" if temp > 85 or vib > 0.9 else ("WARNING" if temp > 75 or vib > 0.7 else "NORMAL")
    
    new_entry = MachineLog(machine_id=m_id, temperature=temp, vibration=vib, status=mode)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"status": mode}), 201

@app.route('/export_report/<m_id>')
def export_report(m_id):
    logs = MachineLog.query.filter_by(machine_id=m_id).order_by(MachineLog.id.desc()).limit(50).all()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, f"ULTIMATE AUDIT: {m_id}", 1, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    for log in logs:
        pdf.cell(190, 8, f"{log.timestamp} | {log.temperature}C | {log.vibration}G | {log.status}", 0, 1)
    
    path = f"/tmp/{m_id}_report.pdf" 
    pdf.output(path)
    return send_file(path, as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Default port for local, Render will use its own
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)