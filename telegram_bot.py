"""Single-worker Telegram bot with durable conversations and long polling."""
import json
import logging
import os
import signal
import sqlite3
import threading
import time

from dotenv import load_dotenv
from function import calculate_trip, clock, parse_buffer
from geocode_search import validate_place
from services import ServiceError, request_json

log = logging.getLogger(__name__)


class Bot:
    def __init__(self, token, database='bot.sqlite3', stop=None):
        if not token or ':' not in token:
            raise ValueError('Set TELEGRAM_BOT_TOKEN to a valid bot token.')
        self.base = f'https://api.telegram.org/bot{token}'
        self.db = sqlite3.connect(database)
        self.db.execute('CREATE TABLE IF NOT EXISTS sessions (chat INTEGER PRIMARY KEY, data TEXT, updated REAL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS checkpoint (id INTEGER PRIMARY KEY CHECK(id=1), offset INTEGER)')
        self.db.commit()
        self.stop = stop if stop is not None else threading.Event()

    def api(self, method, data):
        result = request_json('POST', f'{self.base}/{method}', json=data, timeout=(5, 40))
        if not isinstance(result, dict) or result.get('ok') is not True:
            raise ServiceError('Telegram is unavailable. Please try again shortly.')
        return result.get('result')

    def send(self, chat, text):
        self.api('sendMessage', {'chat_id': chat, 'text': text})

    def handle_message(self, chat, text):
        self.db.execute('DELETE FROM sessions WHERE updated < ?', (time.time() - 86400,))
        row = self.db.execute('SELECT data FROM sessions WHERE chat=?', (chat,)).fetchone()
        state = json.loads(row[0]) if row else None
        text = text.strip()
        command = text.casefold().rstrip('!.,')
        if command == '/cancel':
            self.send(chat, 'Trip cancelled. Say hi to plan another trip.')
            self.db.execute('DELETE FROM sessions WHERE chat=?', (chat,))
            return
        if command in ('hi', 'hello', 'hey', '/start', '/help') or state is None:
            state = {'step': 'origin'}
            reply = ("Hi! I'll help you work out when to leave. "
                     "I'll ask for your starting point, destination, arrival time, and buffer.\n\n"
                     'Where are you starting from? Include the city/country.\n'
                     'Use /cancel to cancel, or say hi to start again.')
        else:
            try:
                step = state['step']
                if step == 'origin':
                    state['origin'] = validate_place(text)
                    state['step'] = 'destination'
                    reply = 'Where are you going? Include the city/country.'
                elif step == 'destination':
                    state['destination'] = validate_place(text)
                    state['step'] = 'arrival'
                    reply = 'What time do you want to arrive? Use your local time in 24-hour HH:MM format, for example 09:30.'
                elif step == 'arrival':
                    state['arrival'] = clock(text)
                    state['step'] = 'buffer'
                    reply = 'How many extra minutes would you like as a buffer? Send a whole number, for example 15, or 0 for no buffer (maximum 1440).'
                else:
                    buffer = parse_buffer(text)
                    reply = calculate_trip(state['origin'], state['destination'], state['arrival'], buffer)
                    reply = (f"Your trip: {state['origin']} → {state['destination']}\n"
                             f"Arrival: {clock(state['arrival'])} | Buffer: {buffer} minutes\n\n"
                             f'{reply}\n\nSay hi to plan another trip.')
                    self.send(chat, reply)
                    self.db.execute('DELETE FROM sessions WHERE chat=?', (chat,))
                    return
            except (ValueError, ServiceError) as exc:
                self.send(chat, str(exc))
                return
        self.send(chat, reply)
        self.db.execute('INSERT OR REPLACE INTO sessions VALUES (?, ?, ?)', (chat, json.dumps(state), time.time()))

    def process(self, update):
        # Commit state and offset together only after handling succeeds.
        with self.db:
            message = update.get('message', {})
            chat = message.get('chat', {})
            if chat.get('type') == 'private' and isinstance(message.get('text'), str):
                self.handle_message(chat['id'], message['text'])
            self.db.execute('INSERT OR REPLACE INTO checkpoint VALUES (1, ?)', (update['update_id'] + 1,))

    def run(self, on_progress=None):
        delay = 1
        try:
            while not self.stop.is_set():
                try:
                    row = self.db.execute('SELECT offset FROM checkpoint WHERE id=1').fetchone()
                    params = {'timeout': 30, 'allowed_updates': ['message']}
                    if row:
                        params['offset'] = row[0]
                    updates = self.api('getUpdates', params)
                    if not isinstance(updates, list):
                        raise ServiceError('Invalid Telegram response.')
                    if on_progress:
                        on_progress()
                    for update in updates:
                        if self.stop.is_set():
                            break
                        self.process(update)
                        if on_progress:
                            on_progress()
                    delay = 1
                except ServiceError:
                    # Do not log request exceptions: Telegram URLs contain the token.
                    log.warning('External service failure; retrying in %s seconds', delay)
                    self.stop.wait(delay)
                    delay = min(delay * 2, 60)
        finally:
            self.db.close()


def start():
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    bot = Bot(os.getenv('TELEGRAM_BOT_TOKEN'), os.getenv('DATABASE_PATH', 'bot.sqlite3'))
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: bot.stop.set())
    bot.run()


if __name__ == '__main__':
    start()
