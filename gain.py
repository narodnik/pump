#!/usr/bin/python
import json
import os
import pprint
import sys
import tabulate
import datetime
from colorama import Fore, Back, Style

def get_month_name(month_number):
    month = datetime.date(2022, month_number, 1).strftime('%b')
    return month

def load_exercise_data(exercise):
    workouts = []

    try:
        dir_contents = os.listdir("workouts")
    except FileNotFoundError:
        return []

    for filename in dir_contents:
        # Skip random files from syncthing
        if not filename.startswith("workout_"):
            continue

        date = filename[len("workout_"):][:6]
        day, month, year = int(date[:2]), int(date[2:4]), int(date[4:])
        index = year * 10000 + month * 100 + day
        date = (day, month, year)

        with open(f"workouts/{filename}") as fd:
            info = json.load(fd)
        for i, section in enumerate(info):
            if section["exercise"] == exercise:
                workouts.append((index, date, i, section))
                #pprint.pprint(section)

    workouts.sort(key=lambda w: w[0])
    return workouts

def display_exercise_table(exercise):
    workouts = load_exercise_data(exercise)

    row_max_len = 0

    table = []
    for _, date, index, data in workouts:
        day, month, year = date
        month = get_month_name(month)
        date = "%02d %s %s" % (day, month, year)

        index = Style.DIM + str(index + 1) + Style.RESET_ALL

        row = [date, index]

        # Want to show interset reps
        for i, set in enumerate(data["workout"]):
            #if i > 0:
            #    rest_time = int(set["rest"] / 60)
            #    rest_time = Style.DIM + str(rest_time) + Style.RESET_ALL
            #    row.append(rest_time)
            reps = set["reps"]
            #rest = set["rest"]
            weight = set["weight"]
            weight = Fore.GREEN + str(weight) + Style.RESET_ALL
            row.extend([weight, reps])

        if len(row) > row_max_len:
            row_max_len = len(row)

        table.append(row)

    headers = ["Date", "#"]
    for i in range(0, row_max_len):
        headers.extend([f"Weight {i + 1}", "Reps"])

    # Only display when there's actual data
    if len(workouts):
        print(tabulate.tabulate(table, headers=headers))

def main(argv):
    if len(argv) != 2:
        print("gain EXERCISE")
        return -1

    exercise = argv[1]
    display_exercise_table(exercise)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

