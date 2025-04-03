from datetime import datetime, timedelta
import csv
import json
import argparse
from abc import ABC, abstractmethod
import time
import functools

def timer(func):
    #@functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function {func.__name__} executed in {execution_time:.2f} seconds")
        return result
    return wrapper

class Time:
    def __init__(self, year, month, day):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)

    def upd_date(self):
        return datetime(self.year, self.month,self.day)

class Converter(Time):                      
    def __init__(self, year, month, day, time_str):
        super().__init__(year, month, day)
        self.time_str = time_str

    def convert_time(self):
        date = self.upd_date()

        if self.time_str == '':
            return None

        hours = int(self.time_str[:2])
        minutes = int(self.time_str[2:])

        if hours == 24:
            hours = 0
            date += timedelta(days=1)

        return datetime(date.year, date.month, date.day, hours, minutes).isoformat()

class FileWriter:
    def __init__(self,namefile):
        self.namefile = namefile

    def write(self, header, data):    
        pass

class CsvWrite(FileWriter):                   
    def write(self, header, data):
        with open(self.namefile,mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data)

class JsonWrite(FileWriter):
    def write(self,header, data):
        with open(self.namefile, mode='w') as file:
            json.dump([dict(zip(header, row)) for row in data], file, indent=1)

#csv_file = "/Users/admin/Desktop/git_rep/study_python/201507_flightsjs_copy.csv"
#out_csv = "/Users/admin/Desktop/git_rep/study_python/formatted_time_update.csv"
#out_json = "/Users/admin/Desktop/git_rep/study_python/flights_update.json"

@timer
def process_data(input_file):
    with open(input_file,mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)

        columns_to_delete = ['YEAR', 'MONTH', 'DAY']
        idx_to_delete = [header.index(col) for col in columns_to_delete]
        
        new_header = []
        for i in range(len(header)):
            if i not in idx_to_delete:
                new_header.append(header[i])

        time_columns = ['SCHEDULED_DEPARTURE', 'DEPARTURE_TIME', 'WHEELS_OFF', 'WHEELS_ON', 'SCHEDULED_ARRIVAL',
                    'ARRIVAL_TIME']

        index = [new_header.index(col) for col in time_columns]

        final_data = []

        for row in reader:
            year = row[0]
            month = row[1]
            day = row[2]
            
            new_row = []
            for i in range(len(row)):
                if i not in idx_to_delete: 
                    new_row.append(row[i])
            
            for idx in index:
                converter = Converter(year, month, day, new_row[idx])
                new_row[idx] = converter.convert_time()

            final_data.append(new_row)
            
    return new_header, final_data


if __name__ == "__main__":
    def main():
        parser = argparse.ArgumentParser(description="Flight data converter")
        parser.add_argument("csv_file", help="Path to input CSV file")
        parser.add_argument("output_file", help="Name of output file")
        parser.add_argument("--format", required=True)
        args = parser.parse_args()

        new_header, processed_data = process_data(args.csv_file)
        
        if args.format not in ['csv', 'json']:
            print("Wrong output format, choose .csv or .json")
        elif args.format == 'csv':
            writer = CsvWrite(args.output_file)
            writer.write(new_header, processed_data)
        else:  
            writer = JsonWrite(args.output_file)
            writer.write(new_header, processed_data)

    main()


# python3 date_conv.py 201507_flights.csv flights_update.csv --format csv
# python3 date_conv.py 201507_flights.csv flights_update.json --format json

#test
# python3 date_conv.py 201507_flights.csv flights_update.json --format parquet 




