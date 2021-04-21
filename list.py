import json
import pprint
import sys

def main(argv):
    if len(argv) != 2:
        print("list FILENAME")
        return -1

    filename = argv[1]
    with open(filename) as fd:
        info = json.load(fd)

    pprint.pprint(info)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

