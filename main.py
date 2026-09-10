from function import clock, travel_time, latest_time, distance

## INPUT
origin = input("Enter your origin: ")
destination = input("Enter your destination: ")
arrival_time = clock(input("What time do you want to reach your destination? "))
buffer = clock(input("How much buffer time do you want (minutes)? "))


## OUTPUT
print (f"Distance is {distance(origin, destination)} km")
print(f"Travel Time is {(travel_time(origin, destination))} Minutes")
print(f"You Will Arrive at {clock(arrival_time)} With a Buffer of {clock(buffer)} Minutes")
print(f"You need to start your trip at {clock(latest_time(arrival_time, buffer, origin, destination))}")