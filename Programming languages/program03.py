import csv
import re
import os
import math
import datetime
import zipfile

ORDERS_CSV = '/Users/admin/Desktop/git_rep/Programming languages/orders.csv'
orders = []

with open(ORDERS_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        orders.append(row)

for order in orders:
    hour = order['order_hour_of_day']
    if re.match(r'^(0[5-9]|10)$', hour):
        order['morning_order'] = 'yes'
    else:
        order['morning_order'] = 'no'

start_date = datetime.date(2000, 1, 1)
for order in orders:
    days = order.get('days_since_prior_order')
    if days != '':
        try:
            days = int(float(days))
        except ValueError:
            days = 0
    else:
        days = 0
    order['date_ordered'] = (start_date + datetime.timedelta(days=days)).isoformat()

count_dow_3 = math.fsum(1 for order in orders if order['order_dow'] == '3')
print(f"Total number of orders with order_dow == 3: {int(count_dow_3)}")

os.makedirs('reports', exist_ok=True)

with zipfile.ZipFile('orders.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(ORDERS_CSV)

output_csv = os.path.join('reports', 'orders_with_new_columns.csv')
with open(output_csv, 'w', newline='', encoding='utf-8') as f:
    fieldnames = list(orders[0].keys())
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(orders)

