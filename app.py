import os, requests, datetime, random
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF
from flasgger import Swagger # Professional Documentation

app = Flask(__name__)
app.secret_key = 'sentinel_ultimate_2026'
swagger = Swagger(app) # Initializes Swagger at /apidocs

# --- 1. DB CONFIG ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sentinel_ultimate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MachineLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.String(50))
    temperature = db.Column(db.Float)
    vibration = db.Column(db.Float) # New Variable
    status = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

with app.app_context():
    db.create_all()

# --- 2. CONFIG ---
TOKEN = "8826977337:AAG3b8caO_1g0Mh4Ub_KPT3Ipv1cKbVjDTY"
CHAT_ID = "7201797239"
CURRENT_OTP = "123456"

# --- 3. ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == "Pravallika" and request.form.get('password')== "Princy_@2115":
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
    """Get all machine IDs
    ---
    responses:
      200:
        description: A list of unique machine IDs
    """
    machines = db.session.query(MachineLog.machine_id).distinct().all()
    return jsonify([m[0] for m in machines])

@app.route('/get_data/<m_id>')
def get_data(m_id):
    """Get telemetry history for a machine
    ---
    parameters:
      - name: m_id
        in: path
        type: string
        required: true
    """
    logs = MachineLog.query.filter_by(machine_id=m_id).order_by(MachineLog.id.desc()).limit(20).all()
    return jsonify([{"time": l.timestamp.strftime("%H:%M:%S"), "temp": l.temperature, "vib": l.vibration, "status": l.status} for l in reversed(logs)])

@app.route('/ingest', methods=['POST'])
def ingest():
    """Ingest Real-time Telemetry
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            machine_id:
              type: string
            temperature:
              type: number
            vibration:
              type: number
    """
    data = request.json
    m_id, temp, vib = data.get("machine_id"), data.get("temperature"), data.get("vibration", 0.5)
    
    # Advanced Logic: Emergency if Temp > 85 OR Vibration > 0.9
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
    
    path = f"audit_report.pdf"
    pdf.output(path)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(port=5000, debug=True)