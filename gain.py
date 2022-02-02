import json
import os
import pprint
import sys
import tabulate
import datetime

def get_month_name(month_number):
    month = datetime.date(2022, month_number, 1).strftime('%b')
    return month

def load_exercise_data(exercise):
    workouts = []

    for filename in os.listdir("workouts"):
        # Skip random files from syncthing
        if not filename.startswith("workout_"):
            continue

        date = filename[len("workout_"):][:6]
        day, month, year = int(date[:2]), int(date[2:4]), int(date[4:])
        index = year * 10000 + month * 100 + day
        date = (day, month, year)

        with open(f"workouts/{filename}") as fd:
            info = json.load(fd)
        for section in info:
            if section["exercise"] == exercise:
                workouts.append((index, date, section))
                #pprint.pprint(section)

    workouts.sort(key=lambda w: w[0])
    return workouts

def main(argv):
    if len(argv) != 2:
        print("gain EXERCISE")
        return -1

    exercise = argv[1]
    workouts = load_exercise_data(exercise)

    table = []
    for _, date, data in workouts:
        day, month, year = date
        month = get_month_name(month)
        date = "%02d %s %s" % (day, month, year)

        row = [date]

        # Want to show interset reps
        for i, set in enumerate(data["workout"]):
            reps = set["reps"]
            rest = set["rest"]
            weight = set["weight"]
            row.extend([weight, reps])

        table.append(row)

    headers = ["Date"]
    for i in range(1, 8):
        headers.extend(["Weight %i" % i, "Reps"])

    print(tabulate.tabulate(table, headers=headers))

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

