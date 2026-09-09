import os
import requests
import datetime
import random
import time

from dotenv import load_dotenv

from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    session,
    send_file
)

from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "sentinel-ultra-local-secret"
)


# ============================================================
# DATABASE
# ============================================================

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" +
    os.path.join(basedir, "sentinel_ultra.db")
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ============================================================
# MACHINE TELEMETRY TABLE
# ============================================================

class MachineLog(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    machine_id = db.Column(
        db.String(50)
    )

    temperature = db.Column(
        db.Float
    )

    vibration = db.Column(
        db.Float
    )

    status = db.Column(
        db.String(20)
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.datetime.now
    )


# Create database/table automatically
with app.app_context():
    db.create_all()


# ============================================================
# TELEGRAM CONFIGURATION
# ============================================================

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


# Send normal telemetry every 10 seconds
TELEGRAM_INTERVAL = 10


# Remember last Telegram message for each machine
LAST_TELEGRAM_UPDATE = {}


# Emergency alert cooldown
EMERGENCY_COOLDOWN = 30


# ============================================================
# TELEGRAM FUNCTION
# ============================================================

def send_telegram_msg(text):

    if not TOKEN or not CHAT_ID:

        print(
            "⚠️ Telegram credentials missing."
        )

        return False


    url = (
        f"https://api.telegram.org/"
        f"bot{TOKEN}/sendMessage"
    )


    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }


    try:

        response = requests.post(
            url,
            json=payload,
            timeout=10
        )


        print(
            f"☁️ Telegram API: "
            f"{response.status_code}"
        )


        if response.status_code != 200:

            print(
                f"Telegram response: "
                f"{response.text}"
            )


        return response.status_code == 200


    except requests.exceptions.RequestException as error:

        print(
            f"❌ Telegram connection error: "
            f"{error}"
        )

        return False


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user = request.form.get("username")
        password = request.form.get("password")


        if (
            user == "pravallika"
            and password == "UMMADI"
        ):

            session["logged_in"] = True

            return redirect(
                url_for("index")
            )


        return render_template(
            "login.html",
            error=(
                "Invalid Credentials. "
                "Please use the credentials provided."
            )
        )


    return render_template("login.html")


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def index():

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    return render_template(
        "dashboard.html"
    )


# ============================================================
# GET ALL MACHINES
# ============================================================

@app.route("/get_machines")
def get_machines():

    if not session.get("logged_in"):

        return jsonify([]), 401


    machines = (
        db.session
        .query(MachineLog.machine_id)
        .distinct()
        .all()
    )


    machine_list = [
        machine[0]
        for machine in machines
        if machine[0]
    ]


    return jsonify(machine_list)


# ============================================================
# GET LATEST 20 READINGS
# ============================================================

@app.route("/get_data/<m_id>")
def get_data(m_id):

    if not session.get("logged_in"):

        return jsonify([]), 401


    logs = (
        MachineLog.query
        .filter_by(machine_id=m_id)
        .order_by(MachineLog.id.desc())
        .limit(20)
        .all()
    )


    logs.reverse()


    result = []


    for log in logs:

        result.append({

            "time": log.timestamp.strftime(
                "%H:%M:%S"
            ),

            "temp": log.temperature,

            "vib": log.vibration,

            "status": log.status

        })


    return jsonify(result)


# ============================================================
# INGEST TELEMETRY
# ============================================================

@app.route("/ingest", methods=["POST"])
def ingest():

    data = request.get_json(
        silent=True
    ) or {}


    machine_id = data.get(
        "machine_id"
    )

    temperature = data.get(
        "temperature"
    )

    vibration = data.get(
        "vibration",
        0.5
    )


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if machine_id is None:

        return jsonify({
            "error": "machine_id is required"
        }), 400


    if temperature is None:

        return jsonify({
            "error": "temperature is required"
        }), 400


    try:

        temperature = float(
            temperature
        )

        vibration = float(
            vibration
        )

    except (TypeError, ValueError):

        return jsonify({
            "error": "temperature and vibration must be numbers"
        }), 400


    # --------------------------------------------------------
    # MACHINE STATUS
    # --------------------------------------------------------

    if (
        temperature > 85
        or vibration > 0.90
    ):

        status = "EMERGENCY"

    elif (
        temperature > 75
        or vibration > 0.70
    ):

        status = "WARNING"

    else:

        status = "NORMAL"


    # --------------------------------------------------------
    # SAVE TO DATABASE
    # --------------------------------------------------------

    new_entry = MachineLog(

        machine_id=machine_id,

        temperature=temperature,

        vibration=vibration,

        status=status

    )


    db.session.add(
        new_entry
    )

    db.session.commit()


    # --------------------------------------------------------
    # TELEGRAM LIVE MESSAGE
    # --------------------------------------------------------

    now = time.time()

    last_message_time = (
        LAST_TELEGRAM_UPDATE.get(
            machine_id,
            0
        )
    )


    seconds_since_last = (
        now - last_message_time
    )


    send_message = False


    # Emergency:
    # send immediately, but don't spam every 2 seconds

    if status == "EMERGENCY":

        if seconds_since_last >= EMERGENCY_COOLDOWN:

            send_message = True


    # Normal / Warning:
    # send live update every 10 seconds

    elif seconds_since_last >= TELEGRAM_INTERVAL:

        send_message = True


    if send_message:

        if status == "NORMAL":

            emoji = "🟢"

        elif status == "WARNING":

            emoji = "🟠"

        else:

            emoji = "🚨"


        message = (
            f"{emoji} SENTINEL ULTRA\n\n"
            f"🏭 Machine: {machine_id}\n"
            f"🌡️ Temperature: {temperature:.1f} °C\n"
            f"📳 Vibration: {vibration:.2f} G\n"
            f"⚠️ Status: {status}\n"
            f"🕐 Time: "
            f"{datetime.datetime.now().strftime('%H:%M:%S')}\n\n"
            f"☁️ Cloud monitoring: ACTIVE"
        )


        if send_telegram_msg(message):

            LAST_TELEGRAM_UPDATE[
                machine_id
            ] = now


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return jsonify({

        "status": status,

        "machine_id": machine_id,

        "temperature": temperature,

        "vibration": vibration

    }), 201


# ============================================================
# PDF REPORT
# ============================================================

@app.route("/export_report/<m_id>")
def export_report(m_id):

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    logs = (
        MachineLog.query
        .filter_by(machine_id=m_id)
        .order_by(MachineLog.id.desc())
        .limit(50)
        .all()
    )


    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        "B",
        16
    )


    pdf.cell(
        190,
        10,
        f"INDUSTRIAL AUDIT: {m_id}",
        1,
        1,
        "C"
    )


    pdf.ln(10)


    pdf.set_font(
        "Arial",
        size=10
    )


    for log in logs:

        line = (
            f"{log.timestamp} | "
            f"{log.temperature:.1f}C | "
            f"{log.vibration:.2f}G | "
            f"{log.status}"
        )


        pdf.cell(
            190,
            8,
            line,
            0,
            1
        )


    filename = (
        f"{m_id}_audit_report.pdf"
    )


    path = os.path.join(
        "/tmp",
        filename
    )


    pdf.output(path)


    return send_file(
        path,
        as_attachment=True,
        download_name=filename
    )


# ============================================================
# TELEGRAM TEST
# ============================================================

@app.route("/test_bot")
def test_bot():

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    result = send_telegram_msg(
        "🚀 SENTINEL ULTRA\n\n"
        "Telegram connection is working!\n"
        "☁️ Cloud monitoring: ACTIVE"
    )


    if result:

        return "Telegram test sent successfully."

    return (
        "Telegram test failed. "
        "Check TELEGRAM_TOKEN and "
        "TELEGRAM_CHAT_ID."
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )


    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )