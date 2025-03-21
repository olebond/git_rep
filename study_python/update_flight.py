import csv
import json

csv_file = "/Users/admin/Desktop/git_repo/study_python/201507_flightsjs.csv"
upd_flights = "/Users/admin/Desktop/git_repo/study_python/formatted_time.csv"
json_file = 'flights.json'


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

'''with open(upd_flights, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    for row in formatted_time[1:]:
        writer.writerow(row)
'''

'''with open(json_file, 'w') as jsonfile:
    json.dump([dict(zip(header,row)) for row in formatted_time[1:]],jsonfile, indent=1)
'''
