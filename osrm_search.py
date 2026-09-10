import requests


def osrmSearch():
    reutrn 

def orsmDistance(origin, destination):
    # Construct the OSRM API URL
    url = f"http://router.project-osrm.org/route/v1/driving/{origin[0]},{origin[1]};{destination[0]},{destination[1]}?overview=false"

    # Send a GET request to the OSRM API
    response = requests.get(url)
    data = response.json()

    # Extract the distance from the response (in meters)
    distance_meters = data['routes'][0]['distance']

    # Convert distance to kilometers
    distance_km = distance_meters / 1000.0

    return distance_km


def osrmDuration(origin, destination):
    # Construct the OSRM API URL
    url = f"http://router.project-osrm.org/route/v1/driving/{origin[0]},{origin[1]};{destination[0]},{destination[1]}?overview=false"

    # Send a GET request to the OSRM API
    response = requests.get(url)
    data = response.json()

    # Extract the duration from the response (in seconds)
    duration_seconds = data['routes'][0]['duration']

    # Convert duration to minutes
    duration_minutes = round(duration_seconds / 60.0)

    return duration_minutes