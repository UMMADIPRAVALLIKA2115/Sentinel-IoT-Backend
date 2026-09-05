# Sentinel-IoT: Industrial Machine Health Monitoring & Visualization 🚀🏭

Sentinel-IoT is a **Full-Stack Industry 4.0 solution** designed for real-time machine health monitoring. By bridging the gap between raw hardware telemetry and actionable human intelligence, this system provides a live dashboard for data visualization and an automated cloud-alerting layer for emergency response.

---

## 📊 Live Dashboard Preview
*(Recruiter Tip: Watch the real-time line chart and mobile alerts in action below)*

https://github.com/UMMADIPRAVALLIKA2115/Sentinel-IoT-Backend/blob/main/dashboard.html%20-%20Sentinel-IoT-Backend-main%20-%20Visual%20Studio%20Code%202026-09-05%2011-41-40.mp4?raw=true

> **Note:** For more project updates, visit my [LinkedIn Profile](https://linkedin.com/in/ummadipravallika/).

---

## 🛠 Features (v2.0)
- **Real-Time Data Ingestion:** Built a robust Flask-based REST API to handle JSON payloads from IoT edge devices.
- **Dynamic Visualization:** Integrated **Chart.js** to build an auto-updating frontend dashboard that visualizes temperature trends.
- **Three-Stage Monitoring Logic:**
  - 🟢 **Normal:** Systems stable (<70°C).
  - 🟡 **Warning:** High-temperature detected (70°C - 85°C).
  - 🔴 **Emergency:** Critical overheating (>85°C) triggers instant **Telegram Bot API** alerts.
- **Data Persistence:** Automated CSV logging to maintain a historical audit trail.
- **Security-First Design:** Implemented environment variables (`.env`) to protect sensitive API credentials.

---

## 💻 Tech Stack
- **Backend:** Python 3.x, Flask
- **Frontend:** HTML5, Bootstrap 5, Chart.js
- **API/Communication:** REST APIs, Telegram Bot API, JSON
- **Tools:** VS Code, Git, Industrial Machine Simulator, Dotenv

---

## 📂 Project Structure
```text
Sentinel-IoT/
├── app.py                  # Central Flask Backend (The Brain)
├── device_simulator.py      # IoT Machine Simulator (Data Source)
├── .env                    # Secret API Credentials (HIDDEN)
├── .gitignore              # Ensures security by hiding secrets
├── requirements.txt        # Project Dependencies
├── templates/              # UI Folder
│   └── dashboard.html      # Real-time Visualization Dashboard
└── machine_logs.csv        # Historical Health Data
