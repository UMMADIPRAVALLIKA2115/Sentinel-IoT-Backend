import json
import random
import time
import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = "factory/machine01/telemetry"

def create_mqtt_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="IoT_Machine_Simulator")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
        return client
    except Exception as e:
        print(f"MQTT Warning: {e}. Simulator running in direct mode.")
        return None

def generate_telemetry(force_anomaly=False):
    if force_anomaly or random.random() < 0.05:
        # Anomaly / Overheating state
        temp = round(random.uniform(86.0, 98.0), 2)
        vibration = round(random.uniform(4.5, 8.5), 2)   # High vibration (mm/s)
        pressure = round(random.uniform(40.0, 55.0), 2)  # High pressure (PSI)
        rpm = random.randint(1850, 2200)                 # Over-speed
        current = round(random.uniform(20.0, 28.0), 2)  # High current draw (A)
    else:
        # Normal to warning operating range
        temp = round(random.uniform(62.0, 84.0), 2)
        vibration = round(random.uniform(0.8, 3.2), 2)
        pressure = round(random.uniform(28.0, 36.0), 2)
        rpm = random.randint(1450, 1750)
        current = round(random.uniform(11.0, 16.0), 2)

    return {
        "machine_id": "PUMP-01",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "temperature": temp,
        "vibration": vibration,
        "pressure": pressure,
        "rpm": rpm,
        "current": current
    }

def main():
    client = create_mqtt_client()
    if client:
        client.loop_start()

    print("🚀 IoT Edge Device Simulator Started... Publishing telemetry every 2s.")
    try:
        while True:
            payload = generate_telemetry()
            json_payload = json.dumps(payload)
            print(f"📡 Publishing: {json_payload}")

            if client and client.is_connected():
                client.publish(MQTT_TOPIC, json_payload)

            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping Simulator...")
        if client:
            client.loop_stop()
            client.disconnect()

if __name__ == "__main__":
    main()
