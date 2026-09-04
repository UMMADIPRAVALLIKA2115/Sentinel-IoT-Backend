import requests
TOKEN = "8826977337:AAF,......"
CHAT_ID = "720....." 

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {
    "chat_id": CHAT_ID, 
    "text": "Hello Pravallika HAVE A GOOD DAY! ✅"
}

print("Connecting to Telegram...")
response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())