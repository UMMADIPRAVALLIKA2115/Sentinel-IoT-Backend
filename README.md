# Sentinel-IoT: Industrial Machine Health Monitoring System 🚀🏭

Sentinel-IoT is a Python-based backend architecture designed for **Industry 4.0** (Smart Manufacturing). It enables real-time ingestion of industrial sensor data and triggers automated emergency notifications via the Telegram Bot API when critical anomalies—such as machine overheating—are detected.

---

## 📺 Project Demo
*(Tip: Once you upload the video to LinkedIn, take a screenshot of your code and the Telegram alert and paste the image here!)*

---

## 🛠 Features
- **Real-time RESTful Ingestion:** Built a Flask-based API endpoint to handle high-frequency JSON payloads from IoT edge devices.
- **Multi-Mode Monitoring Logic:** 
  - 🟢 **Normal:** Systems are stable (<70°C).
  - 🟡 **Warning:** High-temperature detection (70°C - 85°C) with console logging.
  - 🔴 **Emergency:** Critical overheating (>85°C) triggers instant Telegram push notifications.
- **Automated Data Persistence:** Implemented CSV data logging to track historical machine health for predictive maintenance analysis.
- **Security-First Configuration:** Uses environment variables (`.env`) to protect sensitive API tokens and credentials.

---

## 💻 Tech Stack
- **Backend:** Python 3.x, Flask (REST Framework)
- **Communications:** Telegram Bot API, HTTP/JSON
- **Data:** CSV (File-based logging)
- **Tools:** VS Code, Git, Industrial Simulator

---

## 🏗 System Architecture
1. **IoT Simulator:** A Python script simulating an industrial CNC machine sending temperature data.
2. **Flask Backend:** The central ingestion engine that processes incoming REST requests.
3. **Logic Engine:** Analyzes data streams to identify anomalies based on industrial safety thresholds.
4. **Notification Layer:** Connects to the Telegram Cloud to deliver zero-latency alerts to site engineers.

---

## 📖 Setup & Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/UMMADIPRAVALLIKA2115/Sentinel-IoT.git
   cd Sentinel-IoT
