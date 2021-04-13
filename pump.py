import json
import os
import pprint
import time
from datetime import datetime, timedelta

exercises = [
    ("b",   "bench_press",      "Bench press"),
    ("i",   "incline_press",    "Incline press"),
    ("s",   "shoulder_press",   "Shoulder press"),
    ("d",   "dumbbell_press",   "Dumbbell press"),
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

def save_exercise(exercise, rows):
    session.append({"exercise": exercise, "workout": rows})

def save_session():
    pprint.pprint(session)
    try:
        os.mkdir("workouts")
    except FileExistsError:
        pass
    now = datetime.now()
    filename = "workouts/workout_%02d%02d.wkt" % (now.day, now.month)
    with open(filename, "w") as fd:
        json.dump(session, fd)

start = time.time()

def entry():
    global start

    for key, tag in keymap.items():
        print("%s [%s]" % (descs[tag], key))
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

    rows = []
    while True:
        print("[f] finish [c] cancel")
        i = 1
        reps = input("Set %s reps> " % i)

        if reps == "c":
            return CONTINUE
        elif reps == "f":
            save_exercise(exercise, rows)
            return CONTINUE

        end = time.time()
        elapsed = end - start
        print("%s elapsed." % format_elapsed_time(elapsed))
        start = end

        rows.append({"reps": reps, "rest": elapsed})
        i += 1

while True:
    if entry() == EXIT:
        break

