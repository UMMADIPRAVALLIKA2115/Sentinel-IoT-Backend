import requests, time, random

# CHANGE THIS TO YOUR RENDER URL
URL = "https://sentinel-iot-backend-5.onrender.com/ingest"

machines = ["CNC-HYD-001", "LATHE-HYD-002", "DRILL-HYD-003"]

print("🚀 Sentinel IoT Simulator Started...")
print(f"Sending data to: {URL}")

while True:
    for m_id in machines:
        temp = random.uniform(50, 95)
        vib = random.uniform(0.1, 1.0)
        
        payload = {
            "machine_id": m_id,
            "temperature": round(temp, 2),
            "vibration": round(vib, 2)
        }
        
        try:
            res = requests.post(URL, json=payload, timeout=5)
            print(f"Sent: {m_id} | Temp: {round(temp,1)}C | Status: {res.status_code}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            
    time.sleep(5) # Send data every 5 seconds