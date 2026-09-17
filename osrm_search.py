import math
import os
from services import ServiceError, request_json


def osrmSearch(origin, destination):
    base = os.getenv('ROUTING_URL', 'https://router.project-osrm.org').rstrip('/')
    data = request_json('GET', f'{base}/route/v1/driving/{origin[0]},{origin[1]};{destination[0]},{destination[1]}',
                        params={'overview': 'false'})
    try:
        if data['code'] != 'Ok':
            raise ValueError
        route = data['routes'][0]
        meters, seconds = float(route['distance']), float(route['duration'])
        if not all(math.isfinite(v) and v >= 0 for v in (meters, seconds)):
            raise ValueError
        return round(meters / 1000, 2), math.ceil(seconds / 60)
    except (KeyError, IndexError, TypeError, ValueError):
        raise ServiceError('No valid driving route was found for these locations.') from None
