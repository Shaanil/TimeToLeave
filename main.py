from function import calculate_trip, clock

## INPUT
origin = input("Enter your origin: ")
destination = input("Enter your destination: ")
arrival_time = clock(input("What time do you want to reach your destination? "))
buffer = clock(input("How much buffer time do you want (minutes)? "))

## OUTPUT
message = calculate_trip(origin, destination, arrival_time, buffer)

for n in message:
    print (n)