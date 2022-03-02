import sys
from tabulate import tabulate

def show_relative_intensity_table(weight, reps):
    # (2, 0.95)
    # (8, 0.80)

    gain = (0.8 - 0.95) / (8 - 2)
    inter = 0.8 - gain*8

    relative_intensity = gain * reps + inter
    print(f"relative_intensity: {relative_intensity:.3f}")
    onerm = weight / relative_intensity
    print(f"1rm: {onerm:.2f}")
    table = []
    for desired_reps in range(6, 13):
        desired_intensity = gain * desired_reps + inter
        recommend = desired_intensity * onerm
        table.append((desired_reps, f"{recommend:.2f}"))
    headers = ["Desired reps", "Recommended weight"]
    print(tabulate(table, headers=headers))

def main(argv):
    if len(argv) != 3:
        print("reps WEIGHT REPS", file=sys.stderr)
        return -1

    weight = int(argv[1])
    reps = int(argv[2])

    show_relative_intensity_table(weight, reps)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

