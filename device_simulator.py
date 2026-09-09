import requests
import time
import random

# LOCAL FLASK SERVER
URL = "https://sentinel-iot-backend-17.onrender.com/ingest"

machines = [
    "CNC-HYD-001",
    "LATHE-HYD-002"
]

while True:

    for m_id in machines:

        temperature = random.randint(60, 95)
        vibration = round(random.uniform(0.1, 1.0), 2)

        payload = {
            "machine_id": m_id,
            "temperature": temperature,
            "vibration": vibration
        }

        try:

            response = requests.post(
                URL,
                json=payload,
                timeout=5
            )

            print(
                f"📡 Sent to Local Server: "
                f"{m_id} | "
                f"Temp: {temperature}°C | "
                f"Vibration: {vibration}G | "
                f"Status: {response.status_code}"
            )

        except requests.exceptions.RequestException as error:

            print(
                f"❌ Flask server unavailable: {error}"
            )

    time.sleep(2)