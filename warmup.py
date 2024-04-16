#!/usr/bin/python
import sys
import tabulate

def print_stats(first, bar):
    table = []
    for i, ratio in enumerate([0.5, 0.7, 0.9, 1.0]):
        weight = ratio * first
        pct = ratio * 100
        table.append((f"{pct:.0f}", weight, (weight - bar) / 2))
    print(tabulate.tabulate(table, headers=["percent", "total weight", "plates"]))

def main(argv):
    if len(argv) != 2:
        print("error: missing FIRST_REP argument", file=sys.stderr)
        return -1

    first = float(argv[1])

    # Olympic bar = 20 kg
    print("Olympic bar (=20 kg):")
    print_stats(first, 20)
    print()

    print("Ez curl bar (=8.6 kg):")
    print_stats(first, 8.6)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

