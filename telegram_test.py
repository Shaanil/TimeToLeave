"""Compatibility entry point. Tests never send messages to a real Telegram user."""
if __name__ == '__main__':
    import unittest
    unittest.main(module=None, argv=['unittest', 'discover', '-s', 'tests'])
