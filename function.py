from osrm_search import orsmDistance ,osrmDuration
from geocode_search import geocode
import requests

##Inputs Needed: 
# Distance
# Arrival Time
# Buffer Time

### Speed is a Factor to be Analyse
# Time to be claculated in Minutes for claculations

def calculate_trip(origin, destination, arrival_time, buffer):
    distance_km = distance(origin, destination)
    travel_time_minutes = travel_time(origin, destination)
    latest_start_time = latest_time(arrival_time, buffer, origin, destination)

    return distance_km, travel_time_minutes, latest_start_time

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



def latest_time(arrival_time, buffer, origin, destination):
    est_arrival_time = arrival_time - travel_time(origin, destination) - buffer  

    if est_arrival_time < 0:
        est_arrival_time += 24 * 60  # Add 24 hours in minutes to wrap around to the previous day

    elif est_arrival_time >= 24 * 60:
        est_arrival_time -= 24 * 60  # Subtract 24 hours in minutes to wrap around to the next day

    else:
        est_arrival_time = est_arrival_time  # No adjustment needed
    return est_arrival_time


def travel_time (origin, destination):
    osrm_duration = osrmDuration(geocode(origin), geocode(destination))
    return osrm_duration


def distance(origin, destination):
    osrm_Distance = orsmDistance(geocode(origin), geocode(destination))
    return osrm_Distance