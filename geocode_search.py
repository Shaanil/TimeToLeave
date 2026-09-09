import requests

def geocode(place):
    response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={
            "q": place,
            "format": "json",
            "limit": 1
        },
        headers={"User-Agent": "TimeToLeave"}
    )

    result = response.json()[0]
    return float(result["lon"]), float(result["lat"])


