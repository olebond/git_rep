from __future__ import annotations

import argparse

from .converter import process_flights, write_csv, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert flight HHMM columns into ISO datetimes.")
    parser.add_argument("input_file", help="Path to source flight CSV file")
    parser.add_argument("output_file", help="Path to output CSV or JSON file")
    parser.add_argument("--format", choices=("csv", "json"), required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    header, rows = process_flights(args.input_file)

    if args.format == "csv":
        write_csv(args.output_file, header, rows)
    else:
        write_json(args.output_file, header, rows)


if __name__ == "__main__":
    main()
