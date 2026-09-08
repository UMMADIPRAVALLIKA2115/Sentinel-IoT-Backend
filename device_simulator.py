import requests, time, random

# CHANGE THIS TO YOUR LIVE RENDER URL
URL = "https://sentinel-iot-backend-5.onrender.com/ingest"

machines = ["CNC-HYD-001", "LATHE-HYD-002", "DRILL-HYD-003"]

print("🚀 Sentinel IoT Simulator Started...")
print(f"Sending data to: {URL}")

while True:
    for m_id in machines:
        payload = {
            "machine_id": m_id,
            "temperature": round(random.uniform(50, 95), 2),
            "vibration": round(random.uniform(0.1, 1.0), 2)
        }
        
        try:
            res = requests.post(URL, json=payload, timeout=5)
            print(f"Sent: {m_id} | Status: {res.status_code}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            
    time.sleep(5) # Send data every 5 seconds