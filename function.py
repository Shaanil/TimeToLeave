##Inputs Needed: 
# Distance
# Arrival Time
#  Buffer Time

maximum_speed = 100  # Maximum speed in km/h
avg_speed = int(maximum_speed * 0.6 )



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


def latest_time(arrival_time, buffer):
    est_arrival_time = arrival_time - buffer
    return est_arrival_time


def travel_time(distance):
    return distance / avg_speed *60  # Convert hours to minutes

def distance(origin, destination):
    # Ask Google Routes API for the route
    # Get distanceMeters from response
    # Convert meters → kilometers
    distance =0
    return distance_km
