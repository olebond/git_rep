#!/usr/bin/env python3
import os
import csv
import psycopg2
from psycopg2 import sql

def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", 5432)),
        database=os.getenv("PG_DATABASE", "mydb"),
        user=os.getenv("PG_USER", "myuser"),
        password=os.getenv("PG_PASSWORD", "mysecretpassword")
    )
    conn.autocommit = True
    return conn


def create_airport_dim_table(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS airport_dim;")
    cur.execute("""
    CREATE TABLE airport_dim (
        airport_seq_id INTEGER,
        airport_id INTEGER,
        airport TEXT,
        display_airport_name TEXT,
        display_airport_city_name_full TEXT,
        airport_wac INTEGER,
        airport_country_name TEXT,
        airport_country_code_iso TEXT,
        airport_state_name TEXT,
        airport_state_code TEXT,
        airport_state_fips TEXT,
        city_market_id INTEGER,
        display_city_market_name_full TEXT,
        city_market_wac INTEGER,
        lat_degrees INTEGER,
        lat_hemisphere TEXT,
        lat_minutes INTEGER,
        lat_seconds INTEGER,
        latitude DOUBLE PRECISION,
        lon_degrees INTEGER,
        lon_hemisphere TEXT,
        lon_minutes INTEGER,
        lon_seconds INTEGER,
        longitude DOUBLE PRECISION,
        utc_local_time_variation TEXT,
        airport_start_date TEXT,
        airport_thru_date TEXT,
        airport_is_closed SMALLINT,
        airport_is_latest SMALLINT
    );
    """)
    cur.close()


def load_airport_dim(conn, csv_path):
    cur = conn.cursor()
    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header row
        # Prepare insert with placeholders
        placeholders = ", ".join(["%s"] * len(header))
        insert_sql = sql.SQL("INSERT INTO airport_dim VALUES ({});").format(sql.SQL(placeholders))
        for row in reader:
            if not row:
                continue
            # Convert empty strings to None
            row = [None if v == '' else v for v in row]
            cur.execute(insert_sql, row)
    cur.close()


def aggregate_top5(conn):
    cur = conn.cursor()
    query = """
    SELECT state, airline, flights_count
    FROM (
        SELECT a.airport_state_name AS state,
               flights.airline,
               COUNT(*) AS flights_count,
               ROW_NUMBER() OVER (PARTITION BY a.airport_state_name ORDER BY COUNT(*) DESC) AS rn
        FROM flights
        JOIN airport_dim 
          ON flights.origin_airport = airport_dim.airport
        WHERE airport_dim.airport_country_name = 'United States'
          AND airport_dim.airport_is_latest = 1
        GROUP BY airport_dim.airport_state_name, flights.airline
    ) sub
    WHERE rn <= 5
    ORDER BY state, flights_count DESC;
    """
    cur.execute(query)
    results = cur.fetchall()
    cur.close()

    print("State | Airline | Flight Count")
    for state, airline, count in results:
        print(f"{state} | {airline} | {count}")


def main():
    # Update this path if CSV is located elsewhere
    airport_csv_path = os.getenv("T_MASTER_CORD_CSV", "study_sql/T_MASTER_CORD.csv")
    
    conn = get_connection()
    
    # Create and load airport_dim table
    create_airport_dim_table(conn)
    load_airport_dim(conn, airport_csv_path)
    
    # Run aggregation
    aggregate_top5(conn)
    conn.close()


if __name__ == "__main__":
    main() 