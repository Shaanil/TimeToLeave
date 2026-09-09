from function import clock, travel_time, latest_time

## INPUT
distance_km = float(input("How long is the distance (km)? "))
arrival_time = clock(input("What time do you want to reach your destination? "))
buffer = clock(input("How much buffer time do you want (minutes)? "))


## OUTPUT
print (f"Distance is {distance_km} km")
print (f"Arrival Time is {clock(arrival_time)}")
print(f"Travel Time is {clock(travel_time(distance_km))}")
print(f"Latest Time to Start is {clock(latest_time(arrival_time, buffer))}")