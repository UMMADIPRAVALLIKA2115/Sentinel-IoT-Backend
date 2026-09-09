import requests, time, random

# CHANGE THIS TO YOUR ACTUAL RENDER LINK
URL = "https://sentinel-iot-backend.onrender.com/ingest"

machines = ["CNC-HYD-001", "LATHE-HYD-002"]

while True:
    for m_id in machines:
        payload = {"machine_id": m_id, "temperature": random.randint(60, 95), "vibration": round(random.uniform(0.1, 1.0), 2)}
        try:
            r = requests.post(URL, json=payload)
            print(f"📡 Sent to Cloud: {m_id} | {r.status_code}")
        except: print("Cloud Offline")
    time.sleep(3)