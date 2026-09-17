import unittest
from unittest.mock import patch
import requests
from function import clock, parse_buffer, calculate_trip
from services import ServiceError, request_json
from telegram_bot import Bot
from osrm_search import osrmSearch


class TripTests(unittest.TestCase):
    def test_time_validation(self):
        self.assertEqual(clock('23:59'), 1439)
        for value in ('24:00', '12:60', '9', '-1:00', ''):
            with self.assertRaises(ValueError):
                clock(value)
        self.assertEqual(parse_buffer('15'), 15)
        for value in ('-1', '1.5', '00:15', '1441'):
            with self.assertRaises(ValueError):
                parse_buffer(value)

    @patch('function.distance', return_value=(20, 30.2))
    def test_previous_day_and_rounding(self, _):
        result = calculate_trip('A', 'B', 15, 10)
        self.assertIn('23:34 (1 day(s) before arrival)', result)

    @patch('osrm_search.request_json')
    def test_route_validation(self, request):
        request.return_value = {'code': 'Ok', 'routes': [{'distance': 1000, 'duration': 61}]}
        self.assertEqual(osrmSearch((1, 2), (3, 4)), (1, 2))
        for data in ({'code': 'NoRoute'}, {'code': 'Ok', 'routes': []}, None):
            request.return_value = data
            with self.assertRaises(ServiceError):
                osrmSearch((1, 2), (3, 4))

    @patch('services.requests.request', side_effect=requests.Timeout('secret-token'))
    def test_safe_network_error(self, _):
        with self.assertRaises(ServiceError) as error:
            request_json('GET', 'https://example.com')
        self.assertNotIn('secret-token', str(error.exception))


class BotTests(unittest.TestCase):
    def setUp(self):
        self.bot = Bot('test:token', ':memory:')
        self.sender = patch.object(self.bot, 'send').start()
        self.addCleanup(patch.stopall)
        self.addCleanup(self.bot.db.close)

    def update(self, text, number=1):
        self.bot.process({'update_id': number, 'message': {'chat': {'id': 10, 'type': 'private'}, 'text': text}})

    @patch('telegram_bot.calculate_trip', return_value='Leave by 09:00')
    def test_conversation(self, calculate):
        for number, text in enumerate(('hi', 'Colombo', 'Galle', '10:00', '15')):
            self.update(text, number)
        calculate.assert_called_once_with('Colombo', 'Galle', 600, 15)
        reply = self.sender.call_args.args[1]
        self.assertIn('Colombo → Galle', reply)
        self.assertIn('Arrival: 10:00 | Buffer: 15 minutes', reply)
        self.assertIn('Leave by 09:00', reply)
        self.assertIsNone(self.bot.db.execute('SELECT * FROM sessions').fetchone())
        self.assertEqual(self.bot.db.execute('SELECT offset FROM checkpoint').fetchone()[0], 5)

    def test_greeting_restarts_existing_conversation(self):
        for text in ('hi', 'Colombo', ' Hi! '):
            self.update(text)
        self.assertEqual(self.bot.db.execute('SELECT data FROM sessions').fetchone()[0], '{"step": "origin"}')
        self.assertIn('Where are you starting from?', self.sender.call_args.args[1])

    def test_failed_send_does_not_advance(self):
        self.update('/start', 10)
        self.sender.side_effect = ServiceError('offline')
        with self.assertRaises(ServiceError):
            self.update('Colombo', 11)
        self.assertEqual(self.bot.db.execute('SELECT offset FROM checkpoint').fetchone()[0], 11)
        self.assertIn('origin', self.bot.db.execute('SELECT data FROM sessions').fetchone()[0])

    def test_invalid_input_keeps_step(self):
        for text in ('/start', 'Colombo', 'Galle', '25:00'):
            self.update(text)
        self.assertIn('arrival', self.bot.db.execute('SELECT data FROM sessions').fetchone()[0])
