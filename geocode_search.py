import os
import threading
import time
from functools import lru_cache

from services import ServiceError, request_json

_lock = threading.Lock()
_last_request = 0.0


def validate_place(place):
    if not isinstance(place, str) or not 1 <= len(place.strip()) <= 200:
        raise ValueError('Enter a location between 1 and 200 characters.')
    return place.strip()


@lru_cache(maxsize=512)
def geocode(place):
    global _last_request
    place = validate_place(place)
    # Serialize calls to respect the public Nominatim service's request limit.
    with _lock:
        time.sleep(max(0, 1.1 - (time.monotonic() - _last_request)))
        try:
            data = request_json('GET', os.getenv('GEOCODING_URL', 'https://nominatim.openstreetmap.org/search'),
                                params={'q': place, 'format': 'json', 'limit': 1},
                                headers={'User-Agent': os.getenv('GEOCODING_USER_AGENT', 'TimeToLeave/1.0')})
        finally:
            _last_request = time.monotonic()
    if not isinstance(data, list):
        raise ServiceError('The location service returned an invalid response.')
    if not data:
        raise ServiceError('Location not found. Use /start and enter a more specific address.')
    try:
        lon, lat = float(data[0]['lon']), float(data[0]['lat'])
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError
        return lon, lat
    except (KeyError, TypeError, ValueError):
        raise ServiceError('The location service returned invalid coordinates.') from None
