from dotenv import load_dotenv
import os
import csv
import psycopg2

load_dotenv(dotenv_path="../study_docker/.env")

columns = [
        'airport_seq_id', 'airport_id', 'airport', 'display_airport_name',
        'display_airport_city_name_full', 'airport_wac', 'airport_country_name',
        'airport_country_code_iso', 'airport_state_name', 'airport_state_code',
        'airport_state_fips', 'city_market_id', 'display_city_market_name_full',
        'city_market_wac', 'lat_degrees', 'lat_hemisphere', 'lat_minutes',
        'lat_seconds', 'latitude', 'lon_degrees', 'lon_hemisphere', 'lon_minutes',
        'lon_seconds', 'longitude', 'utc_local_time_variation',
        'airport_start_date', 'airport_thru_date', 'airport_is_closed', 'airport_is_latest'
]

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=int(os.environ["POSTGRES_PORT"]),
    database=os.environ["POSTGRES_DATABASE"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"]
)

def create_airport_dim_table(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS airport_dim (
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

def load_data_from_csv(conn, csv_path):
    cur = conn.cursor()
    sql_query = f"INSERT INTO airport_dim ( {', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    with open("/Users/admin/Desktop/git_rep/study_sql/T_MASTER_CORD.csv", newline='', encoding = 'UTF-8') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [name.lower() for name in reader.fieldnames]
        for row in reader:
            values = [row.get(col) or None for col in columns]
            cur.execute(sql_query, values)
    cur.close()
def main():
    conn.autocommit = True
    create_airport_dim_table(conn)
    load_data_from_csv(conn, "/Users/admin/Desktop/git_rep/study_sql/T_MASTER_CORD.csv")
    conn.close()

if __name__ == "__main__":
    main()
