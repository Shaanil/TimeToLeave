from osrm_search import osrmSearch
from geocode_search import geocode
import requests

##Inputs Needed: 
# Distance
# Arrival Time
# Buffer Time

### Speed is a Factor to be Analyse
# Time to be claculated in Minutes for claculations

def calculate_trip(origin, destination, arrival_time, buffer):
    distance_km, duration_minutes = distance(origin, destination)
    latest_start_time = latest_time(arrival_time, buffer, duration_minutes)

    format_message = [
        (f"Distance is {distance_km} km"),
        (f"Duration is {duration_minutes} Minutes"),
        (f"You need to start your trip at {clock(latest_start_time)} to reach your destination on time."),
        ]
    return format_message

def clock(value):
    if isinstance(value, int) or isinstance(value, float):
        hours = int(int(value)/60)
        minutes = int(value) % 60
        return (f"{hours}:{minutes:02d}")

    elif isinstance(value, str):
        hours = value.split(":")[0]
        minutes = value.split(":")[1]
        return (int(hours) * 60 + int(minutes))

    elif isinstance(value, tuple):
        hours = int(value[0])
        minutes = int(value[1])
        return (hours * 60 + minutes)

def trip_start(reach_time, travel_time):
    return reach_time - travel_time



def latest_time(arrival_time, buffer, duration_minutes):
    est_arrival_time = arrival_time - duration_minutes - buffer

    if est_arrival_time < 0:
        est_arrival_time += 24 * 60  # Add 24 hours in minutes to wrap around to the previous day

    elif est_arrival_time >= 24 * 60:
        est_arrival_time -= 24 * 60  # Subtract 24 hours in minutes to wrap around to the next day

    else:
        est_arrival_time = est_arrival_time  # No adjustment needed
    return est_arrival_time



def distance(origin, destination):
    osrm_Distance, duration_minutes = osrmSearch(geocode(origin), geocode(destination))
    return osrm_Distance, duration_minutes