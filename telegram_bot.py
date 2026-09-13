from dotenv import load_dotenv
import os
import requests

from function import calculate_trip, clock

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Store the current step and answers for each Telegram user.
users = {}


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    response = requests.post(url, json=data)
    return response.json()


def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"

    params = {}
    if offset is not None:
        params["offset"] = offset

    response = requests.get(url, params=params)
    return response.json()


def handle_message(chat_id, text):
    # /start begins the questions again.
    if text == "/start":
        users[chat_id] = {
            "step": "origin",
            "origin": "",
            "destination": "",
            "arrival_time": 0,
            "buffer": 0
        }
        send_message(chat_id, "Enter your origin:")
        return

    # If the user hasn't started the bot yet.
    if chat_id not in users:
        users[chat_id] = {
            "step": "origin",
            "origin": "",
            "destination": "",
            "arrival_time": 0,
            "buffer": 0
        }
        send_message(chat_id, "Enter your origin:")
        return

    user = users[chat_id]

    if user["step"] == "origin":
        user["origin"] = text
        user["step"] = "destination"
        send_message(chat_id, "Enter your destination:")

    elif user["step"] == "destination":
        user["destination"] = text
        user["step"] = "arrival_time"
        send_message(chat_id, "What time do you want to reach your destination?")

    elif user["step"] == "arrival_time":
        try:
            user["arrival_time"] = clock(text)
            user["step"] = "buffer"
            send_message(chat_id, "How much buffer time do you want (minutes)?")
        except Exception:
            send_message(chat_id, "Please enter the arrival time in the format your clock() function expects.")

    elif user["step"] == "buffer":
        try:
            user["buffer"] = clock(text)

            message = calculate_trip(
                user["origin"],
                user["destination"],
                user["arrival_time"],
                user["buffer"]
            )

            send_message(chat_id, message)

            # Reset so the user can start another calculation with /start.
            del users[chat_id]

        except Exception:
            send_message(chat_id, "Please enter a valid buffer time.")


def start():
    offset = None

    while True:
        data = get_updates(offset)

        for update in data.get("result", []):
            offset = update["update_id"] + 1

            message = update.get("message")
            if not message or "text" not in message:
                continue

            chat_id = message["chat"]["id"]
            text = message["text"]

            handle_message(chat_id, text)


if __name__ == "__main__":
    start()