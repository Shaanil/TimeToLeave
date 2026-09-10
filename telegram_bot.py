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


url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
response = requests.get(url)
data = response.json()

if data["result"]:
    update = data["result"][-1]
    message = update.get("message")

    if message:
        text = message.get("text", "")
        chat_id = message["chat"]["id"]

        if text == "/start":
            send_message(
                chat_id,
                "Welcome to TimeToLeave! 🚗\n\nUse /help to learn how to use the bot."
            )

        elif text == "/help":
            send_message(
                chat_id,
                "TimeToLeave helps you calculate when you should leave for a trip.\n\n"
                "Use /plan to plan a trip."
            )

        elif text == "/plan":
            send_message(
                chat_id,
                "Trip planning is coming next! 🚗\n\n"
                "We will connect this command to calculate_trip()."
            )

        else:
            send_message(
                chat_id,
                "Sorry, I didn't understand. Try /help."
            )

        print("Message:", text)
        print("Chat ID:", chat_id)
else:
    print("No new messages.")