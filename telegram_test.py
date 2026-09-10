from dotenv import load_dotenv
import os
import requests

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = "1502669427"

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

data= {
    "chat_id": CHAT_ID,
    "text": "Hello From TimeToLeave"

}

response = requests.get()
response = requests.post(url, json=data)

print("Status code:", response.status_code)
print("Response:", response.json())