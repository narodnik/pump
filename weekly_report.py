#!/usr/bin/python
import csv
import json
import os
import sys
import tabulate
from datetime import datetime, timedelta

from pump import descs

WEIGHT_CSV = "openscale.csv"
WEEKS = 4

def parse_datestr(datestr):
    day, month, year = int(datestr[:2]), int(datestr[2:4]), int(datestr[4:])
    return datetime(2000 + year, month, day)

def week_dates(date):
    start = date - timedelta(days=date.weekday()) - timedelta(days=(WEEKS - 1) * 7)
    return [start + timedelta(days=i) for i in range(WEEKS * 7)]

def datestr(date):
    return f"{date.day:02d}{date.month:02d}{str(date.year)[2:]}"

def calories_for_date(date):
    filename = f"calories/calorie_{datestr(date)}.wkt"
    if not os.path.isfile(filename):
        return None

    with open(filename) as fd:
        data = json.load(fd)

    total = 0
    for item in data:
        mult = item["amount"] / 100
        fat = item["fat"] * mult
        carb = item["carb"] * mult
        protein = item["protein"] * mult
        total += 9*fat + 4*carb + 4*protein
    return round(total)

def exercises_for_date(date):
    filename = f"workouts/workout_{datestr(date)}.wkt"
    if not os.path.isfile(filename):
        return []

    with open(filename) as fd:
        data = json.load(fd)

    names = []
    for section in data:
        tag = section["exercise"]
        names.append(descs.get(tag, tag))
    return names

def load_weights():
    with open(WEIGHT_CSV) as csvf:
        reader = csv.reader(csvf)
        rows = list(reader)

    headers, rows = rows[0], rows[1:]
    lookup = dict((label, index) for index, label in enumerate(headers))

    weights = []
    for row in rows:
        dt = datetime.strptime(row[lookup["dateTime"]], "%Y-%m-%d %H:%M")
        weight = float(row[lookup["weight"]])
        weights.append((dt, weight))
    weights.sort()
    return weights

def weight_for_date(date, weights):
    day = date.date()
    for dt, weight in weights:
        if dt.date() == day:
            return weight
    return None

def main(argv):
    if len(argv) > 1:
        date = parse_datestr(argv[1])
    else:
        date = datetime.now()

    weights = load_weights()

    table = []
    for day in week_dates(date):
        calories = calories_for_date(day)
        weight = weight_for_date(day, weights)
        exercises = exercises_for_date(day)
        table.append((
            day.strftime("%Y-%m-%d %a"),
            calories if calories is not None else "-",
            f"{weight:.2f}" if weight is not None else "-",
            ", ".join(exercises) if exercises else "-",
        ))

    print(tabulate.tabulate(table, headers=["Day", "Calories", "Weight", "Exercises"]))

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
