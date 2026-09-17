"""Bounded HTTP calls with safe errors (never include credential-bearing URLs)."""
import requests


class ServiceError(Exception):
    pass


def request_json(method, url, **kwargs):
    kwargs.setdefault('timeout', (5, 15))
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        raise ServiceError('An external service is unavailable. Please try again shortly.') from None
