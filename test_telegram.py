import requests
TOKEN = "8826977337:AAG3b8caO_1g0Mh4Ub_KPT3Ipv1cKbVjDTY"
CHAT_ID = "7201797239" 

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {
    "chat_id": CHAT_ID, 
    "text": "Hello Pravallika HAVE A GOOD DAY! ✅"
}

print("Connecting to Telegram...")
response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())