from dotenv import load_dotenv
import os
import requests

from function import calculate_trip

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    response = requests.post(url, json=data)
    return response.json()


def get_update():

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"

    response = requests.get(url)
    data= response.json()

    for i in data["result"]:
        print ()
        print ("Name:",i['message']['chat']['first_name'],
               ", ChatID:",i['message']['chat']['id'],
                ", Date:",i["message"]['date'],
                ", Message:",i["message"]['text'])

#get_update()

send_message(1502669427 ,input("Enter a Message: "))