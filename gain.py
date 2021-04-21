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

    for filename in os.listdir(wdir):
        print(f"{filename}")
        with open(f"{wdir}/{filename}") as fd:
            info = json.load(fd)
        for section in info:
            if section["exercise"] == exercise:
                pprint.pprint(section)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

