import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from server import BotRuntime, make_app


class HealthTests(unittest.TestCase):
    def call(self, healthy, path='/health', method='GET'):
        runtime = Mock()
        runtime.healthy.return_value = healthy
        start = Mock()
        body = b''.join(make_app(runtime)({'PATH_INFO': path, 'REQUEST_METHOD': method}, start))
        return start.call_args.args[0], body

    def test_ready_and_unavailable(self):
        self.assertEqual(self.call(True), ('200 OK', b'{"status": "ok"}'))
        self.assertEqual(self.call(False)[0], '503 Service Unavailable')

    def test_routes_and_methods(self):
        self.assertEqual(self.call(True, '/')[0], '200 OK')
        self.assertEqual(self.call(True, '/missing')[0], '404 Not Found')
        self.assertEqual(self.call(True, method='POST')[0], '405 Method Not Allowed')
        self.assertEqual(self.call(True, method='HEAD'), ('200 OK', b''))

    def test_readiness_requires_recent_poll_and_live_worker(self):
        runtime = BotRuntime('test:token', ':memory:')
        with patch.object(runtime.worker, 'is_alive', return_value=True):
            self.assertFalse(runtime.healthy())
            runtime.progress()
            self.assertTrue(runtime.healthy())
            runtime.last_progress -= 181
            self.assertFalse(runtime.healthy())
            runtime.progress()
            runtime.stop.set()
            self.assertFalse(runtime.healthy())

    @patch('server.Bot', side_effect=RuntimeError('secret token'))
    def test_worker_failure_is_visible_without_leaking_secrets(self, _):
        runtime = BotRuntime('test:token', ':memory:')
        with self.assertLogs('server', level='ERROR') as logs:
            runtime.worker.start()
            runtime.worker.join(timeout=2)
        self.assertTrue(runtime.failed.is_set())
        self.assertFalse(runtime.healthy())
        self.assertNotIn('secret token', ''.join(logs.output))


class ServerSmokeTests(unittest.TestCase):
    def test_http_polling_and_sigterm(self):
        # Real HTTP server + SQLite + bot loop; only Telegram transport is mocked.
        with socket.socket() as candidate:
            candidate.bind(('127.0.0.1', 0))
            port = candidate.getsockname()[1]
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, PORT=str(port), TELEGRAM_BOT_TOKEN='test:token',
                       DATABASE_PATH=str(Path(directory) / 'state' / 'bot.sqlite3'))
            script = '''
from telegram_bot import Bot
def fake_api(self, method, data):
    self.stop.wait(0.05)
    return []
Bot.api = fake_api
from server import main
raise SystemExit(main())
'''
            process = subprocess.Popen([sys.executable, '-c', script], env=env,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       cwd=Path(__file__).resolve().parents[1])
            try:
                deadline = time.monotonic() + 10
                ready = False
                while time.monotonic() < deadline and process.poll() is None:
                    try:
                        with urlopen(f'http://127.0.0.1:{port}/health', timeout=1) as response:
                            ready = json.load(response) == {'status': 'ok'}
                            if ready:
                                break
                    except HTTPError as error:
                        error.close()
                        time.sleep(0.05)
                    except URLError:
                        time.sleep(0.05)
                self.assertTrue(ready, 'HTTP health endpoint never became ready')
                self.assertTrue(Path(env['DATABASE_PATH']).exists())
                process.send_signal(signal.SIGTERM)
                stdout, stderr = process.communicate(timeout=10)
                self.assertEqual(process.returncode, 0, stderr.decode())
                self.assertNotIn(b'test:token', stdout + stderr)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate(timeout=5)

    @patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': ''})
    def test_missing_token_fails_without_starting_http(self):
        with patch('server.load_dotenv'), patch('server.create_server') as http:
            from server import main
            with self.assertLogs('server', level='ERROR'):
                self.assertEqual(main(), 1)
            http.assert_not_called()
