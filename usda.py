#!/usr/bin/python
import os, requests, sys
from tabulate import tabulate

# This is a valid key but you might get rate limited.
# So searches with many pages of results might crash.
# Signup link for a higher limit key: https://fdc.nal.usda.gov/api-key-signup.html
API_KEY = "DEMO_KEY"
if os.path.exists("usda_api_key"):
    API_KEY = open("usda_api_key", "r").read().strip()

if len(sys.argv) == 1:
    print("./usda.py cheddar cheese")
    sys.exit(-1)

query = " ".join(sys.argv[1:])

# to get the food use https://api.nal.usda.gov/fdc/v1/food/######?api_key=DEMO_KEY 
response = requests.get(
    "https://api.nal.usda.gov/fdc/v1/foods/search",
    params={
        "api_key": API_KEY,
        "query": query,
        "dataType": ["Foundation", "Survey (FNDDS)"],
        "pageSize": 200,
    }
)
result = response.json()
pages = result["pageList"]
foods = result["foods"]
for page in pages[1:]:
    response = requests.get(
        "https://api.nal.usda.gov/fdc/v1/foods/search",
        params={
            "api_key": API_KEY,
            "query": query,
            "dataType": ["Foundation", "Survey (FNDDS)"],
            "pageSize": 200,
        }
    )
    result = response.json()
    foods += result["foods"]

table = []
header = ["id", "name", "fat", "carb", "protein"]
for food in foods:
    row = [food["fdcId"], food["description"], None, None, None]
    fat_idx = 2
    carb_idx = 3
    prot_idx = 4
    for nutrient in food["foodNutrients"]:
        match nutrient["nutrientName"]:
            case "Protein":
                row[prot_idx] = nutrient["value"]
            case "Total lipid (fat)":
                row[fat_idx] = nutrient["value"]
            case "Carbohydrate, by difference":
                row[carb_idx] = nutrient["value"]
    table.append(row)

print(tabulate(table, header))
