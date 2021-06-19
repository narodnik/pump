import json
import os
import pprint
import sys

def main(argv):
    if len(argv) != 3:
        print("gain DIR EXERCISE")
        return -1

    wdir = argv[1]
    exercise = argv[2]

    workouts = []

    for filename in os.listdir(wdir):
        print(f"{filename}")

        date = filename[len("workout_"):][:4]
        day, month = int(date[:2]), int(date[2:])
        index = month * 100 + day

        with open(f"{wdir}/{filename}") as fd:
            info = json.load(fd)
        for section in info:
            if section["exercise"] == exercise:
                workouts.append((index, date, section))
                #pprint.pprint(section)

    workouts.sort(key=lambda w: w[0])
    pprint.pprint(workouts)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

