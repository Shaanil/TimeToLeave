from dotenv import load_dotenv
from function import calculate_trip, clock, parse_buffer
from services import ServiceError


def main():
    load_dotenv()
    try:
        origin = input('Enter your origin: ')
        destination = input('Enter your destination: ')
        arrival = clock(input('Arrival time (24-hour HH:MM): '))
        buffer = parse_buffer(input('Buffer time (whole minutes): '))
        print(calculate_trip(origin, destination, arrival, buffer))
        return 0
    except (ValueError, ServiceError) as exc:
        print(f'Error: {exc}')
        return 1
    except (KeyboardInterrupt, EOFError):
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
