import json
import os
import pprint
import sys
import tabulate
import time
from datetime import datetime, timedelta

exercises = [
    ("b",   "bench_press",      "Bench press"),
    ("d",   "deadlift",         "Deadlift"),
    ("s",   "squat",            "Squat"),
    ("i",   "incline_press",    "Incline press"),
    ("sp",  "bb_shoulder_press", "Shoulder press"),
    ("mp",  "military_press",   "Military press"),
    ("lr",  "lat_raises",       "Lat raises"),
    ("dp",  "dumbbell_press",   "Dumbbell press"),
    ("rd",  "romanian_deadlift", "Romanian deadlift"),
    ("ng",  "narrow_grip_bench", "Narrow grip bench press"),
    ("p",   "pullups",          "Pullups"),
    ("h",   "hipthrusts",       "Hipthrusts"),
    ("bc",  "bicep_curls",      "Bicep curls"),
    ("r",   "barbell_rows",     "Rows"),
]

def build_maps():
    keymap = {}
    descs = {}
    for key, exercise_tag, exercise_desc in exercises:
        keymap[key] = exercise_tag
        descs[exercise_tag] = exercise_desc
    return keymap, descs

keymap, descs = build_maps()

CONTINUE = 0
EXIT = 1

def format_elapsed_time(elapsed):
    delta = timedelta(seconds=int(elapsed))
    return str(delta)

session = []
dirname = "workouts"

def save_exercise(exercise, rows):
    session.append({"exercise": exercise, "workout": rows})

def save_session():
    pprint.pprint(session)
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass
    now = datetime.now()
    filename = "%s/workout_%02d%02d.wkt" % (dirname, now.day, now.month)
    with open(filename, "w") as fd:
        json.dump(session, fd)

start = time.time()

def entry():
    global start

    table = []
    current_row = []
    for i, (key, tag) in enumerate(keymap.items()):
        current_row.extend([descs[tag], key])
        if i % 2 == 1:
            table.append(current_row)
            current_row = []
        #print("%s [%s]" % (descs[tag], key))
    print(tabulate.tabulate(table))

    exercise = input("> ")
    if exercise == "x":
        print("Exiting")
        save_session()
        return EXIT
    elif exercise not in keymap:
        print("Invalid exercise.")
        return CONTINUE
    exercise = keymap[exercise]
    print("%s selected" % descs[exercise])

    i = 1
    rows = []
    weight = None
    while True:
        print("[f] finish [c] cancel [r] redo")

        weight_new = input("Weight (%s)> " % weight)
        if weight_new == "c":
            return CONTINUE
        elif weight_new == "f":
            save_exercise(exercise, rows)
            return CONTINUE
        elif weight_new == "r":
            rows.pop()
            continue

        reps = input("Set %s reps> " % i)
        if reps == "c":
            return CONTINUE
        elif reps == "f":
            save_exercise(exercise, rows)
            return CONTINUE
        elif weight_new == "r":
            rows.pop()
            continue

        if weight_new:
            weight = weight_new

        try:
            if weight is not None:
                weight = float(weight)
            reps = float(reps)
        except ValueError:
            print("Invalid input. Retry again.")
            continue

        end = time.time()
        elapsed = end - start
        print("%s elapsed." % format_elapsed_time(elapsed))
        start = end

        rows.append({"reps": reps, "weight": weight, "rest": elapsed})
        i += 1

def main(argv):
    global dirname
    if len(argv) > 1:
        dirname = argv[1]

    while True:
        if entry() == EXIT:
            return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

