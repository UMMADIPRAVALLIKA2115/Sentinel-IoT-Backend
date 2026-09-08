import os, requests, datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sentinel_ultimate_2026')

# --- DB CONFIG (Fixed for Render) ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sentinel_ultimate.db')
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

# --- TELEGRAM CONFIG ---
TOKEN = "8826977337:AAG3b8caO_1g0Mh4Ub_KPT3Ipv1cKbVjDTY"
CHAT_ID = "7201797239"
CURRENT_OTP = "123456"

def send_otp_telegram(otp):
    msg = f"🔐 SENTINEL SECURITY\nYour Verification OTP is: {otp}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == "Pravallika" and request.form.get('password') == "Princy_@2115":
            send_otp_telegram(CURRENT_OTP) # This triggers the OTP
            return redirect(url_for('verify_page'))
    return render_template('login.html')

@app.route('/verify')
def verify_page(): return render_template('verify_otp.html')

@app.route('/verify_logic', methods=['POST'])
def verify_logic():
    if request.form.get('otp') == CURRENT_OTP:
        session['logged_in'] = True
        return redirect(url_for('index'))
    return "Invalid OTP", 401

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
    mode = "NORMAL"
    if temp > 85 or vib > 0.9: mode = "EMERGENCY"
    elif temp > 75 or vib > 0.7: mode = "WARNING"
    new_entry = MachineLog(machine_id=m_id, temperature=temp, vibration=vib, status=mode)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"status": "ok"}), 201

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)