import os, csv, requests, datetime
from flask import Flask, request, jsonify
app = Flask(__name__)
TOKEN = "8826977337:AAF,......"
CHAT_ID = "720....."
LOG_FILE = "machine_logs.csv"

# Function to save data to a CSV file (Excel)
def log_to_csv(m_id, temp, status):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write header if it's a new file
        if not file_exists:
            writer.writerow(["Timestamp", "Machine_ID", "Temperature", "Status"])
        writer.writerow([datetime.datetime.now(), m_id, temp, status])

def send_telegram_alert(m_id, temp):
    message = f"🚨 EMERGENCY: {m_id} is CRITICAL! Temp: {temp}°C"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": message})

@app.route('/ingest', methods=['POST'])
def ingest():
    data = request.json
    m_id = data.get("machine_id", "Unknown")
    temp = data.get("temperature", 0)
    
    # MULTI-MODE LOGIC
    if temp > 85:
        mode = "EMERGENCY"
        send_telegram_alert(m_id, temp)
        print(f"🔴 {mode}: Alert sent for {temp}°C")
    elif temp > 70:
        mode = "WARNING"
        print(f"🟡 {mode}: High temperature detected: {temp}°C")
    else:
        mode = "NORMAL"
        print(f"🟢 {mode}: System stable at {temp}°C")

    # Save everything to the Log File
    log_to_csv(m_id, temp, mode)
    
    return jsonify({"status": mode}), 200

if __name__ == '__main__':
    print("🚀 Multi-Mode Sentinel Backend Active...")
    app.run(port=5000)