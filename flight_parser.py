"""Command-line flight schedule parser."""
import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from csv_loader import parse_files
from validator import load_airports
from query import run_queries

STUDENT_ID = '251RDC067'
FIRST_NAME = 'Matiss'
LAST_NAME = 'Smits'


def read_json(path):
    with open(path, encoding='utf-8') as file:
        return json.load(file)


def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def write_errors(path, errors):
    logger = logging.getLogger('flight_parser')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(path, mode='w', encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(handler)
    try:
        for error in errors:
            logger.warning(error)
    finally:
        logger.removeHandler(handler)
        handler.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Validate and query flight schedules')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('-i')
    source.add_argument('-d')
    source.add_argument('-j')
    parser.add_argument('-a')
    parser.add_argument('-o')
    parser.add_argument('-q')
    parser.add_argument('-r', default='.')
    try:
        args = parser.parse_args(argv)
        if args.j is not None and args.o is not None:
            parser.error('-o cannot be used with -j')
        if args.j is None and args.a is None:
            parser.error('-a is required with -i or -d')
    except SystemExit as error:
        return error.code

    try:
        if args.j is not None:
            db = read_json(args.j)
            if not isinstance(db, list) or not all(isinstance(record, dict) for record in db):
                raise ValueError('Database must be an array of objects')
        else:
            airports = load_airports(args.a)
            if args.i is not None:
                paths = [args.i]
            else:
                paths = sorted(path for path in Path(args.d).iterdir() if path.is_file() and path.name.endswith('.csv'))
                if not paths:
                    raise ValueError('No CSV files in folder')
            db, errors = parse_files(paths, airports)
            output = Path(args.o if args.o is not None else 'db.json')
            write_json(output, db)
            write_errors(output.parent / 'errors.log', errors)
        if args.q is not None:
            queries = read_json(args.q)
            if not isinstance(queries, (dict, list)) or (isinstance(queries, list) and not all(isinstance(q, dict) for q in queries)):
                raise ValueError('Queries must be an object or an array of objects')
            results = run_queries(db, queries)
            stamp = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f'response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{stamp}.json'
            write_json(Path(args.r) / filename, results)
    except (OSError, ValueError, UnicodeError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
