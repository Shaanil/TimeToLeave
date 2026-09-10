from function import calculate_trip, clock, travel_time, latest_time, distance

## INPUT
origin = input("Enter your origin: ")
destination = input("Enter your destination: ")
arrival_time = clock(input("What time do you want to reach your destination? "))
buffer = clock(input("How much buffer time do you want (minutes)? "))

distance_km, travel_time_minutes, latest_start_time = calculate_trip(origin, destination, arrival_time, buffer)

## OUTPUT
print (f"Distance is {distance_km} km")
print(f"Travel Time is {travel_time_minutes} Minutes")
print(f"You Will Arrive at {clock(arrival_time)} With a Buffer of {clock(buffer)} Minutes")
print(f"You need to start your trip at {clock(latest_start_time)} to reach your destination on time.")