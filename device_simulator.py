import requests
import time
import random

URL = "http://127.0.0.1:5000/ingest"

print("🚀 Industrial Machine Simulator Started...")

while True:
    current_temp = random.randint(60, 95)
    payload = {"machine_id": "CNC-HYD-001", "temperature": current_temp}
    try:
        response = requests.post(URL, json=payload)
        if response.status_code == 201:
            print(f"🔥 ALERT! Machine Overheating: {current_temp}°C")
        else:
            print(f"✅ Data Logged: {current_temp}°C")
    except:
        print("❌ Error: Backend is not running! Start app.py first.")
    time.sleep(5)