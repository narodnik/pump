import datetime
import matplotlib.pyplot as plt
import pprint
import sys
from gain import load_exercise_data

# https://www.quora.com/In-bodybuilding-fitness-what-s-the-difference-between-volume-and-intensity-when-it-comes-to-training

def main(argv):
    if len(argv) != 2:
        print("gain EXERCISE")
        return -1

    exercise = argv[1]
    workouts = load_exercise_data(exercise)

    index = []
    values = []
    for _, date, data in workouts:
        day, month, year = date
        date = datetime.date(year, month, day)
        index.append(date)

        #volume = 0
        #for set in data["workout"]:
        #    reps = set["reps"]
        #    weight = set["weight"]
        #    volume += reps * weight
        #values.append(volume)

        weights = [item["weight"] for item in data["workout"]]
        values.append(max(weights))

    fig, ax = plt.subplots()
    ax.plot(index, values)
    ax.grid()
    plt.show()

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

