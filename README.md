# Sentinel-IoT: Industrial Machine Health Monitoring & Visualization 🚀🏭

Sentinel-IoT is a **Full-Stack Industry 4.0 solution** designed for real-time machine health monitoring. It bridges the gap between hardware telemetry and human-readable intelligence by combining a high-performance Python backend with a live data visualization dashboard.

---

## 📊 Live Dashboard Preview
*(Tip: Take a screenshot of your moving line graph and upload it to your GitHub 'media' folder, then replace the link below!)*
![Dashboard Preview](https://via.placeholder.com/800x400.png?text=Show+Your+Moving+Line+Chart+Here)

---

## 🛠 Features (Updated v2.0)
- **Real-Time Data Ingestion:** A Flask-based REST API designed to handle high-frequency JSON payloads from IoT edge devices.
- **Dynamic Web Dashboard:** Integrated **Chart.js** and **Jinja2** to build an auto-updating frontend that visualizes machine temperature trends every 2 seconds.
- **Intelligence & Anomaly Detection:** Server-side logic that categorizes machine states:
  - 🟢 **Normal:** Stable operation.
  - 🟡 **Warning:** Rising temperature trends.
  - 🔴 **Emergency:** Critical overheating (>85°C) triggering instant cloud alerts.
- **Instant Notification Layer:** Fully integrated with the **Telegram Bot API** for mobile emergency alerting.
- **Data Persistence:** Automated CSV logging for historical machine health audits.

---

## 💻 Tech Stack
- **Backend:** Python 3.x, Flask (Micro-framework)
- **Frontend:** HTML5, Bootstrap 5, Chart.js (Data Viz)
- **API/Communication:** REST APIs, Telegram Bot API, JSON
- **Environment:** Dotenv (Security), Requests, IoT Simulator

---

## 📂 Project Structure
```text
Sentinel-IoT/
├── app.py                  # Flask Backend (The Brain)
├── device_simulator.py      # IoT Machine Simulator (The Source)
├── .env                    # Secret API Credentials (HIDDEN)
├── .gitignore              # Protects secrets from being public
├── requirements.txt        # Project Dependencies
├── templates/              # Frontend Folder
│   └── dashboard.html      # Real-time Visualization UI
└── machine_logs.csv        # Historical Data Storage
