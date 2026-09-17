import math
import re
from osrm_search import osrmSearch
from geocode_search import geocode, validate_place
from message import format_trip_results


def parse_buffer(value):
    if not re.fullmatch(r'\d{1,4}', str(value).strip()):
        raise ValueError('Enter buffer minutes as a whole number from 0 to 1440.')
    result = int(value)
    if not 0 <= result <= 1440:
        raise ValueError('Enter buffer minutes as a whole number from 0 to 1440.')
    return result


def clock(value):
    if isinstance(value, str):
        if not re.fullmatch(r'\d{1,2}:\d{2}', value.strip()):
            raise ValueError('Enter a time in 24-hour HH:MM format, for example 09:30.')
        hours, minutes = map(int, value.split(':'))
        if not (0 <= hours < 24 and 0 <= minutes < 60):
            raise ValueError('Time must be between 00:00 and 23:59.')
        return hours * 60 + minutes
    if isinstance(value, tuple) and len(value) == 2:
        return clock(f'{value[0]}:{value[1]:02d}')
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
        minutes = math.floor(value) % 1440
        return f'{minutes // 60:02d}:{minutes % 60:02d}'
    raise ValueError('Invalid time.')


def trip_start(reach_time, travel_time):
    return reach_time - travel_time


def latest_time(arrival_time, buffer, duration_minutes):
    return (arrival_time - buffer - math.ceil(duration_minutes)) % 1440


def distance(origin, destination):
    return osrmSearch(geocode(validate_place(origin)), geocode(validate_place(destination)))


def calculate_trip(origin, destination, arrival_time, buffer):
    if isinstance(arrival_time, bool) or not isinstance(arrival_time, int) or not 0 <= arrival_time < 1440:
        raise ValueError('Arrival time must be a valid time of day.')
    buffer = parse_buffer(buffer)
    distance_km, duration_minutes = distance(origin, destination)
    departure = arrival_time - buffer - math.ceil(duration_minutes)
    days_before = -(departure // 1440)
    label = clock(departure)
    if days_before:
        label += f' ({days_before} day(s) before arrival)'
    return format_trip_results(distance_km, duration_minutes, label)
