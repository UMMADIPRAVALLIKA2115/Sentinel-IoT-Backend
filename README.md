# Sentinel-IoT: Industrial Machine Health Monitoring & Visualization 🚀🏭

Sentinel-IoT is a **Full-Stack Industry 4.0 solution** designed for real-time machine health monitoring. By bridging the gap between raw hardware telemetry and actionable human intelligence, this system provides a live dashboard for data visualization and an automated cloud-alerting layer for emergency response.

---

## 📊 Live Dashboard Preview
*(Recruiter Tip: See the real-time line chart and mobile alerts in action below)*
![Dashboard Preview](https://github.com/UMMADIPRAVALLIKA2115/Sentinel-IoT-Backend/blob/main/media/dashboard_demo.png?raw=true)
> **Note:** For a live video demonstration of the alerting system, visit my [LinkedIn Profile](https://linkedin.com/in/ummadipravallika/).

---

## 🛠 Features (v2.0)
- **Real-Time Data Ingestion:** Built a robust Flask-based REST API to handle high-frequency JSON payloads from IoT edge devices.
- **Dynamic Visualization:** Integrated **Chart.js** to build an auto-updating frontend dashboard that visualizes temperature trends every 2 seconds.
- **Three-Stage Monitoring Logic:**
  - 🟢 **Normal:** Systems stable (<70°C).
  - 🟡 **Warning:** High-temperature detected (70°C - 85°C) with system logging.
  - 🔴 **Emergency:** Critical overheating (>85°C) triggers instant **Telegram Bot API** push notifications.
- **Data Persistence:** Automated CSV logging to maintain a historical audit trail for predictive maintenance analysis.
- **Security-First Design:** Implemented environment variables (`.env`) and `.gitignore` protocols to protect sensitive API credentials.

---

## 💻 Tech Stack
- **Backend:** Python 3.x, Flask
- **Frontend:** HTML5, Bootstrap 5, Chart.js (Data Viz)
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
├── requirements.txt        # Project Dependencies for easy setup
├── templates/              # UI Folder
│   └── dashboard.html      # Real-time Visualization Dashboard
└── machine_logs.csv        # Historical Health Data
