# 1. Export data from openScale app
# 2. Copy to this directory as 'openscale.csv'
# 3. Run this script!

import csv
import matplotlib.pyplot as plt
from tabulate import tabulate
from datetime import datetime

with open("openscale.csv") as csvf:
    reader = csv.reader(csvf)
    rows = list(reader)

headers, rows = rows[0], rows[1:]
lookup = dict((label, index) for index, label in enumerate(headers))

table = []
x_data = []
y_data = []
for row in rows:
    weight_idx = lookup["weight"]
    weight = float(row[weight_idx])

    datetime_idx = lookup["dateTime"]
    dt = row[datetime_idx]
    # 2022-03-22 22:03
    dt = datetime.strptime(dt, "%Y-%m-%d %H:%M")

    table.append((dt, weight))

    x_data.append(dt)
    y_data.append(weight)

print(tabulate(table))

plt.plot(x_data, y_data)
plt.show()

