#!/usr/bin/python
import json, os
import datetime as dt
import tabulate

N = 4

def last_sat():
    now = dt.date.today()
    idx = (now.weekday() + 1) % 7
    sat = now - dt.timedelta(days=7 + idx - 6)
    assert sat.weekday() == 5
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

body_parts = {
    "bb_bench": ["chest"],
    "db_bench": ["chest"],
    "bb_incline_bench": ["chest"],
    "db_incline_bench": ["chest"],
    "cable_fly": ["chest"],
    "cable_low_fly": ["chest"],
    "pause_bench": ["chest"],
    "drop_bench": ["chest"],
    "weighted_pushup": ["chest"],
    "1arm_pushup": ["chest"],

    "deadlift": ["back"],
    "pullup": ["back"],
    "bb_row": ["back"],
    "db_row": ["back"],
    "db_pullover": ["back"],
    "cable_pulldown": ["back"],

    "bb_press": ["shoulders"],
    "db_press": ["shoulders"],
    "bb_military_press": ["shoulders"],
    "kb_overhead_press": ["shoulders"],
    "arnold_press": ["shoulders"],
    "handstand_press": ["shoulders"],
    "front_raise": ["shoulders"],
    "lat_raise": ["shoulders"],
    "kb_halo": ["shoulders"],
    "kb_getup": ["shoulders"],

    "squat": ["legs"],
    "lunge": ["legs"],
    "split_squat": ["legs"],
    "box_squat": ["legs"],
    "smith_machine_squat": ["legs"],
    "hack_squat": ["legs"],
    "hip_thrust": ["legs"],
    "romanian_deadlift": ["legs"],
    "alt_leg_deadlift": ["legs"],
    "kb_deadlift": ["legs"],
    "kb_swing": ["legs"],
    "soleo": ["legs"],
    "leg_press": ["legs"],
    "good_morning": ["legs"],
    "seated_good_morning": ["legs"],
    "kb_getup": ["legs"],

    "bb_curl": ["biceps"],
    "cable_curl": ["biceps"],
    "db_curl": ["biceps"],
    "hammer_curl": ["biceps"],
    "preacher_curl": ["biceps"],
    "incline_curl": ["biceps"],

    "skullcrusher": ["triceps"],
    "cable_pushdown": ["triceps"],
    "cable_overhead_ext": ["triceps"],
    "tricep_kickback": ["triceps"],
    "dips": ["triceps"],
    "diamond_pushup": ["triceps"],
}

week_buckets = [last_sat()]
for i in range(N-1):
    week_buckets.append(week_buckets[-1] - dt.timedelta(weeks=1))
#print(week_buckets)
workouts = load_exercise_data(week_buckets)
# To see all the exercises
#workouts = load_exercise_data(None)
#import pprint
#pprint.pprint(workouts)

bucket_data = {
    "chest": [0, 0, 0, 0],
    "back": [0, 0, 0, 0],
    "shoulders": [0, 0, 0, 0],
    "legs": [0, 0, 0, 0],
    "biceps": [0, 0, 0, 0],
    "triceps": [0, 0, 0, 0],
}

for (exercise, sets) in workouts.items():
    if exercise not in body_parts:
        print(f"Skipping {exercise}!")
        continue
    affected_parts = body_parts[exercise]
    for body_part in affected_parts:
        for i, set_count in enumerate(sets[::-1]):
            bucket_data[body_part][i] += set_count

table = []
headers = ["Body Part", "#"]
for (body_part, buckets) in bucket_data.items():
    for (i, set_count) in enumerate(buckets):
        key = ""
        if i == 0:
            key = body_part

        table.append((key, set_count))
    table.append(("", ""))

print(tabulate.tabulate(table, headers=headers))
