#!/usr/bin/env python3
import os
import csv
import pyodbc

def get_connection():
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={os.getenv("MSSQL_HOST", "localhost")};'
        f'DATABASE={os.getenv("MSSQL_DATABASE", "flights_db")};'
        f'UID={os.getenv("MSSQL_USER", "myuser")};'
        f'PWD={os.getenv("MSSQL_PASSWORD", "mysecretpassword")}'
    )
    conn.autocommit = True
    return conn


def create_airport_dim_table(conn):
    cursor = conn.cursor()
    cursor.execute("IF OBJECT_ID('airport_dim', 'U') IS NOT NULL DROP TABLE airport_dim;")
    cursor.execute("""
    CREATE TABLE airport_dim (
        airport_seq_id INT,
        airport_id INT,
        airport NVARCHAR(255),
        display_airport_name NVARCHAR(255),
        display_airport_city_name_full NVARCHAR(255),
        airport_wac INT,
        airport_country_name NVARCHAR(255),
        airport_country_code_iso NVARCHAR(10),
        airport_state_name NVARCHAR(255),
        airport_state_code NVARCHAR(10),
        airport_state_fips NVARCHAR(10),
        city_market_id INT,
        display_city_market_name_full NVARCHAR(255),
        city_market_wac INT,
        lat_degrees INT,
        lat_hemisphere NVARCHAR(1),
        lat_minutes INT,
        lat_seconds INT,
        latitude FLOAT,
        lon_degrees INT,
        lon_hemisphere NVARCHAR(1),
        lon_minutes INT,
        lon_seconds INT,
        longitude FLOAT,
        utc_local_time_variation NVARCHAR(10),
        airport_start_date NVARCHAR(32),
        airport_thru_date NVARCHAR(32),
        airport_is_closed SMALLINT,
        airport_is_latest SMALLINT
    );
    """)
    cursor.close()


def load_airport_dim(conn, csv_path):
    cursor = conn.cursor()
    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        header = next(reader) 
        placeholders = ", ".join(["?"] * len(header))
        insert_sql = f"INSERT INTO airport_dim VALUES ({placeholders})"
        for row in reader:
            if not row:
                continue
            row = [None if v == '' else v for v in row]
            cursor.execute(insert_sql, row)
    cursor.close()


def aggregate_top5(conn):
    cursor = conn.cursor()
    query = """
    SELECT state, airline, flights_count
    FROM (
        SELECT airport_dim.airport_state_name AS state,
               flights.airline,
               COUNT(*) AS flights_count,
               ROW_NUMBER() OVER (PARTITION BY airport_dim.airport_state_name ORDER BY COUNT(*) DESC) AS rn
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
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    print("State | Airline | Flight Count")
    for state, airline, count in results:
        print(f"{state} | {airline} | {count}")


def main():
    airport_csv_path = os.getenv("T_MASTER_CORD_CSV", "study_sql/T_MASTER_CORD.csv")
    
    conn = get_connection()
    
    create_airport_dim_table(conn)
    load_airport_dim(conn, airport_csv_path)
    
    aggregate_top5(conn)
    conn.close()


if __name__ == "__main__":
    main() 