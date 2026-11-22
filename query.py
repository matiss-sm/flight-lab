"""Validate and execute queries against flight records."""
from validator import KEYS, parse_datetime


def valid_query(query):
    if not isinstance(query, dict):
        return False
    for key, value in query.items():
        if key in ('flight_id', 'origin', 'destination'):
            if not isinstance(value, str):
                return False
        elif key in ('departure_datetime', 'arrival_datetime'):
            if not isinstance(value, str):
                return False
            try:
                parse_datetime(value)
            except ValueError:
                return False
        elif key in ('price', 'min_price'):
            if type(value) not in (int, float):
                return False
        elif key == 'sort_by':
            if value not in KEYS:
                return False
        elif key == 'order':
            if value not in ('asc', 'desc') or 'sort_by' not in query:
                return False
        elif key == 'limit':
            if type(value) is not int or value < 0:
                return False
        else:
            return False
    return True


def matches_query(record, query):
    for key, value in query.items():
        if key in ('flight_id', 'origin', 'destination') and record[key] != value:
            return False
        if key == 'departure_datetime' and record[key] < value:
            return False
        if key == 'arrival_datetime' and record[key] > value:
            return False
        if key == 'price' and not record['price'] <= value:
            return False
        if key == 'min_price' and not record['price'] >= value:
            return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    if not valid_query(query):
        return {'query': query, 'error': 'INVALID_QUERY', 'matches': []}
    matches = [record for record in db if matches_query(record, query)]
    if 'sort_by' in query:
        matches.sort(key=lambda record: record[query['sort_by']], reverse=query.get('order') == 'desc')
    if 'limit' in query:
        matches = matches[:query['limit']]
    return {'query': query, 'matches': matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    if isinstance(queries, dict):
        queries = [queries]
    return [run_query(db, query) for query in queries]
