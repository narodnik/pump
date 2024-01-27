import json, sys, usda
from iterfzf import iterfzf
# adds a food to the db

if len(sys.argv) == 1:
    print("./add-food.py QUERY..")
    sys.exit(-1)

query = " ".join(sys.argv[1:])
info = usda.fetch_food_macros(query)
foods = {}
for id, desc, fat, carb, prot in info:
    foods[desc] = (fat, carb, prot)
select = iterfzf(foods.keys())
if select is None:
    sys.exit(-1)
alias = input(f"alias ({query})> ")
if not alias:
    alias = query
macros = foods[select]

try:
    with open("foods.json") as f:
        foods = json.load(f)
except FileNotFoundError:
    foods = {}

foods[alias] = macros

with open("foods.json", "w") as f:
    json.dump(foods, f, indent=2)

