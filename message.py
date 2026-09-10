
def format_trip_results(distance_km,duration_minutes,latest_start_time):

    format_message = (f"Distance is {distance_km} km\n"
                      f"Duration is {duration_minutes} Minutes\n"
                      f"You need to start your trip at {(latest_start_time)} to reach your destination on time.")
    return format_message
