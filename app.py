import os, requests, datetime, random
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF
from flasgger import Swagger 

# --- 1. SETUP & PATHS ---
# This ensures Render finds your templates and database correctly
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

app.secret_key = os.environ.get('SECRET_KEY', 'sentinel_ultimate_2026')
swagger = Swagger(app) 

# --- 2. DB CONFIG ---
# Using absolute path ensures the database is created in the correct folder on Render
db_path = os.path.join(basedir, 'sentinel_ultimate.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
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

# --- 3. CONFIG ---
TOKEN = "8826977337:AAG3b8caO_1g0Mh4Ub_KPT3Ipv1cKbVjDTY"
CHAT_ID = "7201797239"
CURRENT_OTP = "123456"

# --- 4. ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Use .get() to avoid KeyErrors
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "Pravallika" and password == "Princy_@2115":
            return redirect(url_for('verify_page'))
    return render_template('login.html')

@app.route('/verify')
def verify_page(): 
    return render_template('verify_otp.html')

@app.route('/verify_logic', methods=['POST'])
def verify_logic():
    if request.form.get('otp') == CURRENT_OTP:
        session['logged_in'] = True
        return redirect(url_for('index'))
    return "Invalid OTP", 401

@app.route('/')
def index():
    if not session.get('logged_in'): 
        return redirect(url_for('login'))
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
    if not data:
        return jsonify({"error": "No data"}), 400
    m_id, temp, vib = data.get("machine_id"), data.get("temperature"), data.get("vibration", 0.5)
    
    mode = "NORMAL"
    if temp > 85 or vib > 0.9: mode = "EMERGENCY"
    elif temp > 75 or vib > 0.7: mode = "WARNING"
    
    new_entry = MachineLog(machine_id=m_id, temperature=temp, vibration=vib, status=mode)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"status": "ok"}), 201

@app.route('/export_report/<m_id>')
def export_report(m_id):
    logs = MachineLog.query.filter_by(machine_id=m_id).order_by(MachineLog.id.desc()).limit(50).all()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, f"ULTIMATE AUDIT: {m_id}", 1, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    pdf.cell(50, 10, "Timestamp", 1); pdf.cell(40, 10, "Temp (C)", 1); pdf.cell(40, 10, "Vib (G)", 1); pdf.cell(40, 10, "Status", 1); pdf.ln()
    for log in logs:
        pdf.cell(50, 10, str(log.timestamp), 1)
        pdf.cell(40, 10, str(log.temperature), 1)
        pdf.cell(40, 10, str(log.vibration), 1)
        pdf.cell(40, 10, log.status, 1); pdf.ln()
    
    path = os.path.join(basedir, "audit_report.pdf")
    pdf.output(path)
    return send_file(path, as_attachment=True)

# --- 5. RENDER CONFIG ---
if __name__ == '__main__':
    # This part is critical for Render!
    # It reads the PORT assigned by Render and listens on 0.0.0.0
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)