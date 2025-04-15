import pandas as pd

df = pd.read_csv('flights_update.csv', parse_dates=['DEPARTURE_TIME', 'SCHEDULED_DEPARTURE', 'WHEELS_OFF', 'WHEELS_ON', 'SCHEDULED_ARRIVAL', 'ARRIVAL_TIME'])

column_info = {}

for column in df.columns:
    unique_values = df[column].nunique()
    dtype = str(df[column].dtype)
    null_count = df[column].isnull().sum()
    
    column_info[column] = {
        'dtype': dtype,
        'unique_values': unique_values,
        'null_count': null_count
    }

print("----")
for column, info in column_info.items():
    print(f"{column}")
    print(f"type: {info['dtype']}")
    print(f"unique: {info['unique_values']}")
    print(f"null: {info['null_count']}")
    print("----")

for column, info in column_info.items():
    pg_type = "VARCHAR"
    if info['dtype'] == 'int64':
        pg_type = "INTEGER"
    elif info['dtype'] == 'float64':
        pg_type = "NUMERIC"
    elif 'datetime' in info['dtype']:
        pg_type = "TIMESTAMP"
    
    print(f"{column} {pg_type}") 