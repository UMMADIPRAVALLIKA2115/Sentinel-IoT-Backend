import requests, time, random
URL = "http://127.0.0.1:5000/ingest"
machines = ["CNC-HYD-001", "LATHE-HYD-002"]

while True:
    for m_id in machines:
        payload = {
            "machine_id": m_id,
            "temperature": random.randint(60, 95),
            "vibration": round(random.uniform(0.1, 1.0), 2) # New Vibration data
        }
        try:
            requests.post(URL, json=payload)
            print(f"📡 Sent: {m_id} | {payload['temperature']}C | {payload['vibration']}G")
        except: print("Offline")
    time.sleep(3)