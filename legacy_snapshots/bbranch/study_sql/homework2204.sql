#1_time_on_ground

select
tail_number,
wheels_on,
lead(wheels_off) over (PARTITION BY tail_number order by wheels_on) as next_wheels_off,
lead(wheels_off) over (PARTITION BY tail_number order by wheels_on) - wheels_on as time_on_ground
from flights
order by tail_number, wheels_on;

datediff postgress
age

#2_count_departure

SELECT
  airline,
  COUNT(*) FILTER (WHERE day_of_week = 1 AND departure_time IS NOT NULL) AS "Sun",
  COUNT(*) FILTER (WHERE day_of_week = 2 AND departure_time IS NOT NULL) AS "Mon",
  COUNT(*) FILTER (WHERE day_of_week = 3 AND departure_time IS NOT NULL) AS "Tue",
  COUNT(*) FILTER (WHERE day_of_week = 4 AND departure_time IS NOT NULL) AS "Wed",
  COUNT(*) FILTER (WHERE day_of_week = 5 AND departure_time IS NOT NULL) AS "Thu",
  COUNT(*) FILTER (WHERE day_of_week = 6 AND departure_time IS NOT NULL) AS "Fri",
  COUNT(*) FILTER (WHERE day_of_week = 7 AND departure_time IS NOT NULL) AS "Sat"
FROM flights
where departure_time::date between '2015-07-01' and '2015-07-07'
GROUP BY airline
ORDER BY 2 desc, 3 DESC, 4 DESC, 5 DESC, 6 DESC, 7 DESC, 8 DESC;

сортування по компаніях

pivot  - немає в постгресі pivot, є через фільтр, або через crosstab ( tablefunc)



#3_count_of_flight, total_distance, time_in_air per tail_number
SELECT
  TAIL_NUMBER,
  COUNT(*) AS count_of_flights,
  sum(distance) as total_distance,
  CONCAT(
    FLOOR(EXTRACT(EPOCH FROM SUM(air_time) * INTERVAL '1 minute') / 86400), 'd ',
    FLOOR(MOD(EXTRACT(EPOCH FROM SUM(air_time) * INTERVAL '1 minute'), 86400) / 3600), 'h ',
    FLOOR(MOD(EXTRACT(EPOCH FROM SUM(air_time) * INTERVAL '1 minute'), 3600) / 60), 'm'
  ) AS time_in_air
FROM flights
WHERE departure_time IS NOT NULL
group by TAIL_NUMBER
ORDER BY count_of_flights desc;

time in air ----> timedelta



state, airline ( top 5), flights_count (sort)
join!!

slowly change dimension !











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
               f.airline,
               COUNT(*) AS flights_count,
               ROW_NUMBER() OVER (PARTITION BY a.airport_state_name ORDER BY COUNT(*) DESC) AS rn
        FROM flights f
        JOIN airport_dim a
          ON f.origin_airport = a.airport
        WHERE a.airport_country_name = 'United States'
          AND a.airport_is_latest = 1
        GROUP BY a.airport_state_name, f.airline
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