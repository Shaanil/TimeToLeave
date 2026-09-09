from geocode_search import geocode
import requests

##Inputs Needed: 
# Distance
# Arrival Time
#  Buffer Time

### Speed is a Factor to be Analyse

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
    return est_arrival_time


def travel_time (origin, destination):
    origin = geocode(origin)
    destination = geocode(destination)

    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{origin[0]},{origin[1]};"
        f"{destination[0]},{destination[1]}"
    )

    response = requests.get(url)
    route = response.json()["routes"][0]

    travel_duration = round(route["duration"])  # Convert seconds to minutes and round to 2 decimal places

    return travel_duration


def distance(origin, destination):
    origin = geocode(origin)
    destination = geocode(destination)

    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{origin[0]},{origin[1]};"
        f"{destination[0]},{destination[1]}"
    )

    response = requests.get(url)
    route = response.json()["routes"][0]

    distance_km = round(route["distance"] / 1000, 2)  # Convert cm to km and round to 2 decimal places

    return distance_km