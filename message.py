def format_trip_results(distance_km, duration_minutes, latest_start_time):
    return (f'Distance: {distance_km} km\n'
            f'Estimated driving duration: {duration_minutes} minutes\n'
            f'Leave by {latest_start_time}.\n'
            'Times use your local clock. Estimates exclude live traffic and stops.\n'
            'Map data © OpenStreetMap contributors (https://www.openstreetmap.org/copyright).')
