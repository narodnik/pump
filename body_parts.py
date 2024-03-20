import json, os
import datetime as dt
import tabulate

N = 4

def last_sat():
    now = dt.date.today()
    idx = (now.weekday() + 1) % 7
    sat = now - dt.timedelta(days=7 + idx - 6)
    return sat

def calc_bucket(date):
    return 0

def load_exercise_data(week_buckets):
    workouts = {}

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
        date = dt.date(2000 + year, month, day)

        bucket_idx = None
        for (i, week_start) in enumerate(week_buckets):
            if date >= week_start:
                bucket_idx = i
                break
        if bucket_idx is None:
            continue

        with open(f"workouts/{filename}") as fd:
            info = json.load(fd)
        for i, section in enumerate(info):
            exercise = section["exercise"]
            if exercise not in workouts:
                workouts[exercise] = [0 for _ in range(N)]
            sets = len(section["workout"])
            #print(f"Adding '{exercise}' {sets} sets with date {date} with idx {bucket_idx}")
            assert bucket_idx < N
            workouts[exercise][bucket_idx] += sets

    return workouts

body_parts = [
    ("chest", [
        "bb_bench",
        "db_bench",
        "bb_incline_bench",
        "db_incline_bench",
        "cable_fly",
        "cable_low_fly",
        "pause_bench",
        "drop_bench",
    ]),
    ("back", [
        "deadlift",
        "pullup",
        "bb_row",
        "db_row",
        "db_pullover",
        "cable_pulldown",
    ]),
    ("shoulders", [
        "bb_press",
        "db_press",
        "bb_military_press",
        "arnold_press",
        "handstand_press",
        "front_raise",
        "lat_raise",
    ]),
    ("legs", [
        "squat",
        "lunge",
        "split_squat",
        "box_squat",
        "hip_thrust",
        "romanian_deadlift",
        "alt_leg_deadlift",
        "soleo",
    ]),
    ("biceps", [
        "bb_curl",
        "cable_curl",
        "db_curl",
        "hammer_curl",
        "preacher_curl",
        "incline_curl",
    ]),
    ("triceps", [
        "skullcrusher",
        "cable_pushdown",
        "cable_overhead_ext",
        "dips",
    ]),
]

week_buckets = [last_sat()]
for i in range(N-1):
    week_buckets.append(week_buckets[-1] - dt.timedelta(weeks=1))
#print(week_buckets)
workouts = load_exercise_data(week_buckets)
# To see all the exercises
#workouts = load_exercise_data(None)
#import pprint
#pprint.pprint(workouts)

table = []
headers = ["Body Part", "#", "Sets"]
for (body_part, exercises) in body_parts:
    sets = [0 for _ in range(N)]
    headers.append(body_part)
    for ex in exercises:
        if ex in workouts:
            buckets = workouts[ex]
            assert len(buckets) == len(sets)
            for i in range(N):
                sets[i] += buckets[i]
    for (week, sets_n) in enumerate(sets[::-1]):
        if week == 0:
            b = body_part
        else:
            b = ""
        table.append((b, sets_n))
    table.append(("", ""))

print(tabulate.tabulate(table, headers=headers))
