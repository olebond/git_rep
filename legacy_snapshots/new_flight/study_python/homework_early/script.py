import csv
import random
from datetime import datetime, timedelta

startdate = datetime(2025, 2, 25, 0,0,0 )
enddate = startdate + timedelta(days=7)
current_time = startdate

temp = random.uniform(15,25)
result = []

while current_time < enddate:
    print("LOG", current_time, enddate)
    result.append([current_time, round(temp,1)])
    current_time += timedelta(seconds=1)
    temp += random.uniform(-2,2)
    temp = min(25, max(15, temp))

with open('my_temp.csv', 'w') as file:
    my_temp = csv.writer(file)
    my_temp.writerow(['timestamp', 'temp'])
    #myfile.writerow(result)
    for _ in result:
        my_temp.writerow(_)
