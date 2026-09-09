import os
import json
import sqlite3
import numpy as np
import requests
from flask import Flask, render_template, jsonify, send_file, request
from flask_socketio import SocketIO
from sklearn.ensemble import IsolationForest
from fpdf import FPDF
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sentinel_secret_key')
socketio = SocketIO(app, cors_allowed_origins="*")

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))

DB_FILE = "machine_health.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT,
            timestamp TEXT,
            temperature REAL,
            vibration REAL,
            pressure REAL,
            rpm INTEGER,
            current REAL,
            status TEXT,
            is_anomaly INTEGER,
            rul_hours REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Train Anomaly Detection Model
def build_ml_model():
    X_train = []
    for _ in range(500):
        X_train.append([
            np.random.uniform(60, 75),
            np.random.uniform(0.5, 2.5),
            np.random.uniform(28, 35),
            np.random.randint(1450, 1750),
            np.random.uniform(10, 15)
        ])
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X_train)
    return model

ml_model = build_ml_model()

def calculate_rul(temp, vibration, pressure):
    base_life = 500.0
    strain = ((temp / 100.0) * 0.4) + ((vibration / 10.0) * 0.4) + ((pressure / 60.0) * 0.2)
    return max(0.0, round(base_life * (1.0 - (strain * 0.6)), 1))

def calculate_oee():
    availability, performance, quality = 94.2, 88.5, 99.1
    oee = round((availability * performance * quality) / 10000, 1)
    return {"oee": oee, "availability": availability, "performance": performance, "quality": quality}

def send_telegram_alert(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            print(f"Telegram Alert Error: {e}")

def process_telemetry(data):
    temp = float(data.get('temperature', 0))
    vibration = float(data.get('vibration', 0))
    pressure = float(data.get('pressure', 0))
    rpm = int(data.get('rpm', 0))
    current = float(data.get('current', 0))
    machine_id = data.get('machine_id', 'PUMP-01')
    timestamp = data.get('timestamp')

    # ML Inference
    features = np.array([[temp, vibration, pressure, rpm, current]])
    pred = ml_model.predict(features)[0]
    is_anomaly = 1 if pred == -1 or temp > 85.0 else 0

    if temp > 85.0 or is_anomaly == 1:
        status = "CRITICAL"
    elif temp >= 70.0 or vibration > 4.0:
        status = "WARNING"
    else:
        status = "NORMAL"

    rul = calculate_rul(temp, vibration, pressure)
    oee_data = calculate_oee()

    # Save to SQLite Database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO telemetry (machine_id, timestamp, temperature, vibration, pressure, rpm, current, status, is_anomaly, rul_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (machine_id, timestamp, temp, vibration, pressure, rpm, current, status, is_anomaly, rul))
    conn.commit()
    conn.close()

    enriched_payload = {
        **data,
        "status": status,
        "is_anomaly": is_anomaly,
        "rul_hours": rul,
        **oee_data
    }

    # Stream to WebSockets
    socketio.emit('telemetry_update', enriched_payload)

    # Trigger Telegram Alert
    if status == "CRITICAL":
        alert_msg = (
            f"🚨 <b>CRITICAL ALERT: Sentinel-IoT</b> 🚨\n\n"
            f"<b>Machine:</b> {machine_id}\n"
            f"<b>Status:</b> ANOMALY / OVERHEAT DETECTED\n"
            f"<b>Temperature:</b> {temp}°C\n"
            f"<b>Vibration:</b> {vibration} mm/s\n"
            f"<b>Pressure:</b> {pressure} PSI\n"
            f"<b>RUL Remaining:</b> {rul} Hours\n"
            f"<b>Timestamp:</b> {timestamp}"
        )
        send_telegram_alert(alert_msg)

# MQTT Client setup
def on_mqtt_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        process_telemetry(payload)
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Sentinel_Backend")
mqtt_client.on_message = on_mqtt_message

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.subscribe("factory/+/telemetry")
    mqtt_client.loop_start()
    print("Connected to MQTT Broker listening on factory/+/telemetry")
except Exception as e:
    print(f"MQTT Connection warning: {e}")

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/telemetry', methods=['POST'])
def receive_telemetry_rest():
    data = request.json
    process_telemetry(data)
    return jsonify({"status": "success", "message": "Telemetry processed"}), 200

@app.route('/api/reports/pdf', methods=['GET'])
def generate_pdf_report():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, temperature, vibration, status, rul_hours FROM telemetry ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "Sentinel-IoT: Industrial Machine Health Shift Report", ln=True, align='C')
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 10, f"Generated Report | Machine: PUMP-01", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(45, 8, "Timestamp", 1)
    pdf.cell(30, 8, "Temp (°C)", 1)
    pdf.cell(35, 8, "Vibration", 1)
    pdf.cell(35, 8, "Status", 1)
    pdf.cell(40, 8, "RUL (Hours)", 1)
    pdf.ln()

    pdf.set_font("Helvetica", size=9)
    for row in rows:
        pdf.cell(45, 8, str(row[0]), 1)
        pdf.cell(30, 8, str(row[1]), 1)
        pdf.cell(35, 8, str(row[2]), 1)
        pdf.cell(35, 8, str(row[3]), 1)
        pdf.cell(40, 8, str(row[4]), 1)
        pdf.ln()

    report_path = "shift_report.pdf"
    pdf.output(report_path)
    return send_file(report_path, as_attachment=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)