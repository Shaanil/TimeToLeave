"""Railway entry point: one supervised bot worker and a production HTTP server."""
import json
import logging
import os
from pathlib import Path
import signal
import threading
import time

from dotenv import load_dotenv
from waitress import create_server

from telegram_bot import Bot

log = logging.getLogger(__name__)


class BotRuntime:
    def __init__(self, token, database):
        self.token = token
        self.database = database
        self.stop = threading.Event()
        self.failed = threading.Event()
        self.lock = threading.Lock()
        self.last_progress = None
        self.worker = threading.Thread(target=self.run, name='telegram-bot', daemon=True)

    def progress(self):
        with self.lock:
            self.last_progress = time.monotonic()

    def healthy(self):
        with self.lock:
            recent = self.last_progress is not None and time.monotonic() - self.last_progress < 180
        return recent and self.worker.is_alive() and not self.stop.is_set() and not self.failed.is_set()

    def run(self):
        try:
            # SQLite is created, used and closed on this thread only.
            Path(self.database).parent.mkdir(parents=True, exist_ok=True)
            bot = Bot(self.token, self.database, stop=self.stop)
            bot.run(on_progress=self.progress)
        except Exception as exc:
            # Exception text/tracebacks can contain tokens or personal details.
            log.error('Bot worker failed (%s); restarting the service is required.', type(exc).__name__)
            self.failed.set()
        finally:
            if not self.stop.is_set():
                self.failed.set()


def make_app(runtime):
    def app(environ, start_response):
        method = environ.get('REQUEST_METHOD', 'GET')
        path = environ.get('PATH_INFO', '/')
        headers = [('Content-Type', 'application/json'), ('Cache-Control', 'no-store')]
        if method not in ('GET', 'HEAD'):
            status, payload = '405 Method Not Allowed', {'error': 'method not allowed'}
            headers.append(('Allow', 'GET, HEAD'))
        elif path == '/health':
            healthy = runtime.healthy()
            status = '200 OK' if healthy else '503 Service Unavailable'
            payload = {'status': 'ok' if healthy else 'unavailable'}
        elif path == '/':
            status, payload = '200 OK', {'service': 'TimeToLeave', 'health': '/health'}
        else:
            status, payload = '404 Not Found', {'error': 'not found'}
        body = json.dumps(payload).encode('utf-8')
        headers.append(('Content-Length', str(len(body))))
        start_response(status, headers)
        return [b'' if method == 'HEAD' else body]
    return app


def main():
    load_dotenv()
    os.umask(0o077)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    if not token or ':' not in token:
        log.error('Set TELEGRAM_BOT_TOKEN before starting the server.')
        return 1
    try:
        port = int(os.getenv('PORT', '8080'))
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        log.error('PORT must be an integer between 1 and 65535.')
        return 1

    runtime = BotRuntime(token, os.getenv('DATABASE_PATH', 'bot.sqlite3'))
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: runtime.stop.set())
    try:
        http = create_server(make_app(runtime), host='0.0.0.0', port=port,
                             threads=2, channel_timeout=30, connection_limit=100,
                             max_request_body_size=1024)
    except OSError:
        log.error('Unable to bind the HTTP server port.')
        return 1

    def serve_http():
        try:
            http.run()
        except Exception as exc:
            log.error('HTTP server failed (%s).', type(exc).__name__)
            runtime.failed.set()

    web = threading.Thread(target=serve_http, name='http-server', daemon=True)
    runtime.worker.start()
    web.start()
    log.info('Server listening on port %s; waiting for Telegram polling to become ready.', port)
    result = 0
    try:
        while not runtime.stop.wait(0.5):
            if runtime.failed.is_set() or not runtime.worker.is_alive() or not web.is_alive():
                result = 1
                break
    finally:
        runtime.stop.set()
        http.close()
        runtime.worker.join(timeout=90)
        if runtime.worker.is_alive():
            log.error('Bot did not stop within the shutdown grace period.')
            result = 1
        log.info('Server stopped.')
    return result


if __name__ == '__main__':
    raise SystemExit(main())
