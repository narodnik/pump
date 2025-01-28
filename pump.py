#!/usr/bin/python
import json
import os
import pprint
import sys
import tabulate
import time
from datetime import datetime, timedelta

from gain import display_exercise_table
#from reps import show_relative_intensity_table

def normie_name(name):
    return name.replace(" ", "_")\
               .replace("-", "_")\
               .toLowerCase()\
               .title()

def load_exercises(filename):
    with open(filename) as fd:
        return json.load(fd)
    
def get_all_exercises(exercises):
    all_exercises = []
    for _, exs in exercises.items():
        all_exercises.extend(exs)
    return all_exercises

def build_maps(exercises):
    keymap = {}
    descs = {}
    for key, exercise_tag, exercise_desc in get_all_exercises(exercises):
        keymap[key] = exercise_tag
        descs[exercise_tag] = exercise_desc
    return keymap, descs

CONTINUE = 0
EXIT = 1

def format_elapsed_time(elapsed):
    delta = timedelta(seconds=int(elapsed))
    return str(delta)

dirname = "workouts"

def today_datestr():
    now = datetime.now()
    # We only want the last 2 digits
    year = str(now.year)[2:]
    return f"{now.day:02d}{now.month:02d}{year}"

def today_filename():
    return date_filename(today_datestr())

def date_filename(datestr):
    return f"{dirname}/workout_{datestr}.wkt"

def load_session():
    try:
        with open(today_filename()) as fd:
            return json.load(fd)
    except FileNotFoundError:
        return []

def start_session_exercise(exercise):
    session = load_session()
    session.append({
        "exercise": exercise,
        "workout": []
    })
    save_session(session)

def append_session_exercise(reps, weight, rest, exercise_name):
    session = load_session()
    exercise = session[-1]
    assert exercise["exercise"] == exercise_name
    exercise["workout"].append({
        "reps": reps,
        "weight": weight,
        "rest": rest
    })
    save_session(session)

def cancel_session_last_exercise():
    session = load_session()
    exercise = session[-1]
    if exercise["workout"]:
        print("There are still workouts here! Bailing", file=sys.stderr)
        return
    # Pop the last item off
    session = session[:-1]
    save_session(session)

def redo_session_set():
    session = load_session()
    exercise = session[-1]
    workout = exercise["workout"]
    if not workout:
        print("There are no workouts here! Bailing", file=sys.stderr)
        return
    workout.pop()
    save_session(session)

def get_session_set_index():
    session = load_session()
    exercise = session[-1]
    workout = exercise["workout"]
    return len(workout) + 1

def save_session(session):
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass
    with open(today_filename(), "w") as fd:
        json.dump(session, fd, indent=4)

session_start = time.time()
start = time.time()

def entry(exercises):
    global session_start, start
    keymap, descs = build_maps(exercises)

    table = []
    current_row = []
    idx = 0
    for body_part, exers in exercises.items():
        if idx > 0:
            table.append([])
        for key, _, name in exers:
            current_row.extend([name, key])
            if idx % 2 == 1:
                table.append(current_row)
                current_row = []
            idx += 1
    print(tabulate.tabulate(table))
    print("Other options: custom, resume, show")

    cmd = input("> ")
    if cmd == "x":
        session = load_session()
        pprint.pprint(session, indent=2)
        return EXIT
    elif cmd == "custom":
        exercise = input("Custom exercise> ")
        start_session_exercise(exercise)
    elif cmd == "resume":
        session = load_session()
        exercise = session[-1]["exercise"]
    elif cmd == "show":
        session = load_session()
        pprint.pprint(session, indent=2)
        return CONTINUE
    elif cmd not in keymap:
        print("Invalid exercise.")
        return CONTINUE
    else:
        exercise = keymap[cmd]
        display_exercise_table(exercise)
        print(f"{descs[exercise]} ({exercise}) selected")
        start_session_exercise(exercise)

    weight = None
    reps = None
    while True:
        print("[f] finish [c] cancel [r] redo")

        #if isinstance(weight, float) and isinstance(reps, float):
        #    show_relative_intensity_table(weight, reps)

        weight_new = input("Weight (%s)> " % weight)
        if weight_new == "c":
            cancel_session_last_exercise()
            return CONTINUE
        elif weight_new == "f":
            return CONTINUE
        elif weight_new == "r":
            redo_session_set()
            continue

        reps = input("Set %s reps> " % get_session_set_index())
        if reps == "c":
            cancel_session_last_exercise()
            return CONTINUE
        elif reps == "f":
            return CONTINUE
        elif weight_new == "r":
            redo_session_set()
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
        rest = end - start
        rest_format = format_elapsed_time(rest)
        progress = format_elapsed_time(end - session_start)
        print(f"{rest_format} elapsed. (overall {progress})")
        start = end

        append_session_exercise(reps, weight, rest, exercise)

def main(argv):
    global dirname
    if len(argv) > 1:
        dirname = argv[1]

    exercises = load_exercises("wkt.json")
    while True:
        if entry(exercises) == EXIT:
            return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

