import os
import requests

GOOGLE_MAPS_API_KEY = "AIzaSyAdjKQD8nuzfYSUw6eF6Baw6Zo4vj2AjyE"


def distance(origin, destination):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"
    }

    data = {
        "origin": {
            "address": origin
        },
        "destination": {
            "address": destination
        },
        "travelMode": "DRIVE"
    }

    response = requests.post(url, headers=headers, json=data)

    response.raise_for_status()

    result = response.json()

    distance_meters = result["routes"][0]["distanceMeters"]
    duration_seconds = result["routes"][0]["duration"]
    print(duration_seconds)
    return distance_meters / 1000


print(distance("Negombo, Sri Lanka", "Colombo, Sri Lanka"))  # Example usage
