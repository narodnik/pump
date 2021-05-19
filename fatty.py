import time

filename = "weight.fat"

def main():
    weight = input("weight (kg)> ")
    weight = float(weight)
    timest = int(time.time())
    with open(filename, "a") as f:
        f.write("%d %.1f\n" % (timest, weight))

main()

