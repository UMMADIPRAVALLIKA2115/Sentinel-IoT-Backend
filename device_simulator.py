import requests
import time
import random


# ============================================================
# LOCAL FLASK SERVER
# ============================================================

URL = "https://sentinel-iot-backend-18.onrender.com"


# ============================================================
# 3 MACHINES
# ============================================================

machines = [
    "CNC-HYD-001",
    "LATHE-HYD-002",
    "DRILL-HYD-003"
]


# ============================================================
# LIVE SIMULATION
# ============================================================

while True:

    for machine_id in machines:

        # ----------------------------------------------------
        # Generate live temperature
        # ----------------------------------------------------

        temperature = random.randint(
            60,
            95
        )


        # ----------------------------------------------------
        # Generate live vibration
        # ----------------------------------------------------

        vibration = round(
            random.uniform(
                0.10,
                1.00
            ),
            2
        )


        # ----------------------------------------------------
        # Payload
        # ----------------------------------------------------

        payload = {

            "machine_id": machine_id,

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
                f"{machine_id} | "
                f"Temp: {temperature}°C | "
                f"Vibration: {vibration}G | "
                f"HTTP: {response.status_code}"
            )


        except requests.exceptions.RequestException as error:

            print(
                f"❌ Flask server unavailable: "
                f"{error}"
            )


    # Wait 2 seconds
    time.sleep(2)