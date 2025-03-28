from datetime import datetime, timedelta
import csv
import json
import argparse

class Time:
    def __init__(self, year, month, day):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)

    def upd_date(self):
        return datetime(self.year, self.month,self.day)

class Converter(Time):                      # успадкування
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

class fileWriter:

    def __init__(self,namefile):
        self.namefile = namefile

    def write(self, data):     #абстрактний метод, !використовуватись має в дочірних класах!
        pass

class csvwrite(fileWriter):                   # поліморфізм, write використовується по різному
    def write(self, header, data):
        with open(self.namefile,mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data)

class jsonwrite(fileWriter):
    def write(self,header, data):
        with open(self.namefile, mode='w') as file:
            json.dump([dict(zip(header, row)) for row in data], file, indent=1)

#csv_file = "/Users/admin/Desktop/git_rep/study_python/201507_flightsjs_copy.csv"
#out_csv = "/Users/admin/Desktop/git_rep/study_python/formatted_time_update.csv"
#out_json = "/Users/admin/Desktop/git_rep/study_python/flights_update.json"

def parse_arguments():

    parser = argparse.ArgumentParser(description="Для відкриття будь яких файлів")
    parser.add_argument("csv_file", help="/Users/admin/Desktop/git_rep/study_python/201507_flightsjs_copy.csv")
    parser.add_argument("out_csv", help="/Users/admin/Desktop/git_rep/study_python/formatted_time_update_final.csv")
    parser.add_argument("out_json", help="/Users/admin/Desktop/git_rep/study_python/flights_update_final.json")
    return parser.parse_args()
    #args = parser.parse_args()

def process_data(input_file):
    with open(input_file,mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)

        time_columns = ['SCHEDULED_DEPARTURE', 'DEPARTURE_TIME', 'WHEELS_OFF', 'WHEELS_ON', 'SCHEDULED_ARRIVAL',
                    'ARRIVAL_TIME']

        index = [header.index(col) for col in time_columns]

        final_data = []

        for row in reader:
            year = row[0]
            month = row[1]
            day = row[2]
            for idx in index:
                converter = Converter(year, month, day,row[idx])
                row[idx] = converter.convert_time()

            final_data.append(row)
    return header, final_data

def main():
    args = parse_arguments()

    header, processed_data= process_data(args.csv_file)

    csvwriter = csvwrite(args.out_csv)
    jsonwriter = jsonwrite(args.out_json)

    csvwriter.write(header, processed_data)
    jsonwriter.write(header, processed_data)

if __name__ == "__main__":
    main()

# python3 /Users/admin/Desktop/git_rep/study_python/date_conv.py /Users/admin/Desktop/git_rep/study_python/201507_flightsjs_copy.csv /Users/admin/Desktop/git_rep/study_python/formatted_time_update_final.csv /Users/admin/Desktop/git_rep/study_python/flights_update_final.json







