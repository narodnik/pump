import json, sys
from iterfzf import iterfzf

if len(sys.argv) != 2:
    print("./add-special.py ALIAS")
    sys.exit(-1)

def round_float(v):
    return round(v*100)/100

alias = sys.argv[1]

try:
    with open("foods.json") as f:
        foods = json.load(f)
except FileNotFoundError:
    foods = {}

fat, carb, prot = 0, 0, 0
total = 0

while True:
    select = iterfzf(foods.keys())
    if select is None:
        break
    f, c, p = foods[select]

    while True:
        amount = input(f"{select} amount> ")
        try:
            amount = int(amount)
        except ValueError:
            print("Try again")
            continue
        break

    r = amount/100
    fat += f*r
    carb += c*r
    prot += p*r
    total += amount

if total == 0:
    print("exiting...")
    sys.argv(0)

while True:
    new_total = input(f"{total} total> ")
    if not new_total:
        break
    try:
        total = int(new_total)
    except ValueError:
        print("Try again")
        continue
    break

r = 100/total
f = round_float(fat*r)
c = round_float(carb*r)
p = round_float(prot*r)

foods[alias] = (f, c, p)

with open("foods.json", "w") as f:
    json.dump(foods, f, indent=2)

