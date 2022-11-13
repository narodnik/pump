import json
import os
import pprint
import sys
import tabulate
import time
from datetime import datetime, timedelta

from gain import display_exercise_table
#from reps import show_relative_intensity_table

exercises = [
    [
        "Chest", [

        ("b",   "bb_bench",             "Bench press"),
        ("db",  "db_bench",             "Db bench press"),
        ("i",   "bb_incline_bench",     "Incline bench"),
        ("ib",  "db_incline_bench",     "Db incline bench"),
        ("cf",  "cable_fly",            "Cable fly"),
        ("lcf", "cable_low_fly",        "Low cable fly"),
        ("pb",  "pause_bench",          "Pause bench"),
        ("drp", "drop_bench",           "Drop bench"),
    ]],

    [
        "Back", [

        ("d",   "deadlift",             "Deadlift"),
        ("pp",  "pullup",               "Pullup"),
        ("r",   "bb_row",               "Row"),
        ("dr",  "db_row",               "Db row"),
        ("po",  "db_pullover",          "Db pullover"),
        ("cp",  "cable_pulldown",       "Cable pulldown"),
    ]],

    [
        "Shoulders", [

        ("sp",  "bb_press",             "Shoulder press"),
        ("dp",  "db_press",             "Db shoulder press"),
        ("mp",  "bb_military_press",    "Military press"),
        ("ap",  "arnold_press",         "Arnold press"),
        ("fr",  "front_raise",          "Front raise"),
        ("lr",  "lat_raise",            "Lat raise"),
    ]],

    [
        "Legs", [

        ("s",   "squat",                "Squat"),
        ("l",   "lunge",                "Lunge"),
        ("ss",  "split_squat",          "Split squat"),
        ("bx",  "box_squat",            "Box squat"),
        ("ht",  "hip_thrust",           "Hip thrust"),
        ("rdl", "romanian_deadlift",    "Romanian deadlift"),
        ("asl", "alt_leg_deadlift",     "Alt leg deadlift"),
        ("sol", "soleo",                "Soleo"),
    ]],

    [
        "Biceps", [

        ("bc",  "bb_curl",              "Curl"),
        ("cc",  "cable_curl",           "Cable curl"),
        ("dc",  "db_curl",              "Db curl"),
        ("hc",  "hammer_curl",          "Hammer curl"),
        ("pc",  "preacher_curl",        "Preacher curl"),
        ("ic",  "incline_curl",         "Incline curl"),
    ]],

    [
        "Triceps", [

        ("sk",  "skullcrusher",         "Skullcrusher"),
        ("p",   "cable_pushdown",       "Cable pushdown"),
        ("o",   "cable_overhead_ext",   "Cable overhead ext"),
        ("dip", "dips",                 "Dips"),
    ]],

    [
        "Core", [

        ("hr",  "hanging_raise",        "Hanging raise"),
        ("ws",  "weighted_situp",       "Weighted situp"),
    ]],
    # ("c",   "",                 "Custom"),
]

def get_all_exercises():
    all_exercises = []
    for body_part, exer in exercises:
        all_exercises.extend(exer)
    return all_exercises

def build_maps():
    keymap = {}
    descs = {}
    for key, exercise_tag, exercise_desc in get_all_exercises():
        keymap[key] = exercise_tag
        descs[exercise_tag] = exercise_desc
    return keymap, descs

keymap, descs = build_maps()

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

def entry():
    global session_start, start

    table = []
    current_row = []
    idx = 0
    for body_part, exers in exercises:
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
        print("Exiting")
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

    while True:
        if entry() == EXIT:
            return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

