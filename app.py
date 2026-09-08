import os, requests, datetime, random
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger # 1. Make sure this import is here

app = Flask(__name__)
app.secret_key = 'sentinel_ultimate_2026'

swagger = Swagger(app) # 2. Make sure this line is here!

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = 'sentinel_ultimate_2026'

# --- DB CONFIG ---
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
# Double check these two values!
TOKEN = "8919728098:AAH71DEsykt2KhzQe_nkZD8z8lKxwqMAMcA"
CHAT_ID = "7201797239" 

def send_otp_telegram(otp):
    msg = f"🛡️ SENTINEL ULTRA ACCESS\n\nYour 2FA Verification Code is: {otp}\n\nValid for 5 minutes."
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        # We use a timeout to ensure the website doesn't hang if Telegram is slow
        resp = requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=8)
        return resp.status_code == 200
    except:
        return False

# --- ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        if u == "Pravallika" and p == "Princy_@2115":
            # GENERATE A RANDOM 6-DIGIT OTP
            new_otp = str(random.randint(100000, 999999))
            session['current_otp'] = new_otp # Store it in session to check later
            
            success = send_otp_telegram(new_otp)
            
            if success:
                return redirect(url_for('verify_page'))
            else:
                return render_template('login.html', error="Telegram Gateway Error. Check Bot Connection.")
        
        return render_template('login.html', error="Invalid Industrial Credentials")
    
    return render_template('login.html')

@app.route('/verify')
def verify_page(): 
    return render_template('verify_otp.html')

@app.route('/verify_logic', methods=['POST'])
def verify_logic():
    user_otp = request.form.get('otp')
    # Compare user input to the OTP we stored in the session
    if user_otp == session.get('current_otp'):
        session['logged_in'] = True
        return redirect(url_for('index'))
    return "Invalid OTP Code", 401

@app.route('/')
def index():
    if not session.get('logged_in'): return redirect(url_for('login'))
    return render_template('dashboard.html')

# (Rest of your routes: get_machines, get_data, ingest, export_report remain the same)
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