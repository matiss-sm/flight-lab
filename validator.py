"""Validation and conversion of flight rows."""
import math
import re
from datetime import datetime

KEYS = ('flight_id', 'origin', 'destination', 'departure_datetime', 'arrival_datetime', 'price')


def load_airports(path: str) -> set[str]:
    with open(path, encoding='utf-8') as file:
        return {line for raw in file if (line := raw.strip()) and not line.startswith('#')}


def parse_datetime(value):
    if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}', value):
        raise ValueError('Invalid datetime format')
    return datetime.strptime(value, '%Y-%m-%d %H:%M')


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    if len(fields) != 6:
        return 'WRONG_FIELD_COUNT'
    fields = [field.strip() for field in fields]
    if not all(fields):
        return 'MISSING_FIELD'
    flight_id, origin, destination, departure, arrival, price = fields
    if not re.fullmatch(r'[A-Za-z0-9]{2,8}', flight_id):
        return 'INVALID_FLIGHT_ID'
    if not re.fullmatch(r'[A-Z]{3}', origin) or origin not in airports:
        return 'INVALID_ORIGIN'
    if not re.fullmatch(r'[A-Z]{3}', destination) or destination not in airports:
        return 'INVALID_DESTINATION'
    if origin == destination:
        return 'SAME_ORIGIN_DESTINATION'
    try:
        departure_time = parse_datetime(departure)
    except ValueError:
        return 'INVALID_DEPARTURE'
    try:
        arrival_time = parse_datetime(arrival)
    except ValueError:
        return 'INVALID_ARRIVAL'
    if arrival_time <= departure_time:
        return 'ARRIVAL_NOT_AFTER_DEPARTURE'
    try:
        number = float(price)
    except ValueError:
        return 'INVALID_PRICE'
    if not math.isfinite(number):
        return 'INVALID_PRICE'
    if number <= 0:
        return 'NON_POSITIVE_PRICE'
    return None


def to_record(fields: list[str]) -> dict:
    record = dict(zip(KEYS, (field.strip() for field in fields)))
    record['price'] = float(record['price'])
    return record
