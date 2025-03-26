import csv
import json
from datetime import datetime

csv_file = "/Users/admin/Desktop/git_rep/study_python/201507_flightsjs_copy.csv"
upd_flights = "/Users/admin/Desktop/git_rep/study_python/formatted_time_upd.csv"
json_file = 'flights_upd.json'

def format_time(value):
    if value == '2400' or value = '0000':
        pass
    elif value.isdigit() and len(value) == 4:
        return datetime.strptime(value,"%H%M").strftime("%H:%M")
    return value

with open(csv_file, mode='r') as infile, open(upd_flights, mode='w', newline="") as fin_file:
    reader = csv.reader(infile)
    writer = csv.writer(fin_file)

    header = next(reader)
    writer.writerow(header)

    time_columns = ['SCHEDULED_DEPARTURE', 'DEPARTURE_TIME', 'WHEELS_OFF', 'WHEELS_ON', 'SCHEDULED_ARRIVAL',
                    'ARRIVAL_TIME']
    index = [header.index(col) for col in time_columns]

    json_data = []

    for row in reader:
        for idx in index:
            row[idx] = format_time(row[idx])
        writer.writerow(row)
        json_data.append(dict(zip(header, row)))

with open(json_file,mode='w') as json_fin_file:
    json.dump(json_data, json_fin_file, indent=1)

"""        
def format_time(time):
    return time[:2] + ":" + time[2:]

with open(csv_file, 'r') as file:
    reader = csv.reader(file)              #для прочитання файлу
    header = next(reader)                  #заголовки
    print(header)                          #виводимо заголовки лише

    for i,rows in enumerate(reader):
        print(rows)
        if i == 0:
            break
    time_columns = ['SCHEDULED_DEPARTURE', 'DEPARTURE_TIME', 'WHEELS_OFF', 'WHEELS_ON', 'SCHEDULED_ARRIVAL',
                    'ARRIVAL_TIME']
    index = [header.index(col) for col in time_columns]
    formatted_time = [header]
    for row in reader:
        for id in index:
            row[id] = format_time(row[id])
        formatted_time.append(row)
    #print(formatted_time[1])

with open(upd_flights, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    for row in formatted_time[1:]:
        writer.writerow(row)


'''with open(json_file, 'w') as jsonfile:
    json.dump([dict(zip(header,row)) for row in formatted_time[1:]],jsonfile, indent=1)
'''
"""