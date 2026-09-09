import requests
import time
import random

# LOCAL FLASK SERVER
URL = "http://127.0.0.1:5000/ingest"

# 3 MACHINES
machines = [
    "CNC-HYD-001",
    "LATHE-HYD-002",
    "DRILL-HYD-003"
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
                f"📡 Sent to Cloud: "
                f"{m_id} | "
                f"Temp: {temperature}°C | "
                f"Vibration: {vibration}G | "
                f"{response.status_code}"
            )

        except requests.exceptions.RequestException as error:

            print(
                f"❌ Server unavailable: {error}"
            )

    time.sleep(2)