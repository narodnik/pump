#!/usr/bin/python
import json
import os, sys
import tabulate
from datetime import datetime

from cq_config import meta_foods

# fat, carb, protein
with open("foods.json") as f:
    foods = json.load(f)

dirname = "calories"

def today_datestr():
    now = datetime.now()
    # We only want the last 2 digits
    year = str(now.year)[2:]
    return f"{now.day:02d}{now.month:02d}{year}"

def today_filename():
    return date_filename(today_datestr())

def date_filename(datestr):
    return f"{dirname}/calorie_{datestr}.wkt"

def append_data(data):
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass
    filename = today_filename()
    if os.path.isfile(filename):
        with open(filename, "r") as fd:
            current_data = json.load(fd)
    else:
        current_data = []
    current_data.append(data)
    with open(filename, "w") as fd:
        json.dump(current_data, fd, indent=4)

def get_amount(food):
    while True:
        amount = input(f"Weight ({food})> ")
        try:
            amount = float(amount)
        except ValueError:
            print("Invalid input. Retry again.")
            continue
        return amount

def add_meta(meta_name):
    for food, amount in meta_foods[meta_name].items():
        add_food(food, amount, meta_name)

def add_food(food, amount, desc):
    fat, carb, protein = foods[food]
    append_data({
        "food": food,
        "amount": amount,
        "fat": fat,
        "carb": carb,
        "protein": protein,
    })

def show_summary(datestr):
    filename = date_filename(datestr)
    if not os.path.isfile(filename):
        print(datestr)
        # Nothing to show
        return

    with open(filename, "r") as fd:
        data = json.load(fd)

    table = []
    table_headers = (
        "Food",
        "Amount",
        "Fat",
        "Carb",
        "Protein",
        "Calories"
    )
    total_fat, total_carb, total_protein = 0, 0, 0
    for item in data:
        food = item["food"]
        amount = item["amount"]
        mult = amount / 100
        fat = item["fat"] * mult
        carb = item["carb"] * mult
        protein = item["protein"] * mult
        calorie = 9*fat + 4*carb + 4*protein

        total_fat += fat
        total_carb += carb
        total_protein += protein

        table.append((food, amount, round(fat), round(carb),
                      round(protein), round(calorie)))

    cal_fat, cal_carb, cal_prot = 9*total_fat, 4*total_carb, 4*total_protein
    total_calorie = cal_fat + cal_carb + cal_prot
    table.append(("", "", "", "", "", ""))
    table.append(("Total:", "",
                  round(total_fat), round(total_carb),
                  round(total_protein), round(total_calorie)))
    pct_fat = round(100 * cal_fat / total_calorie)
    pct_carb = round(100 * cal_carb / total_calorie)
    pct_prot = round(100 * cal_prot / total_calorie)
    table.append(("", "", f"{pct_fat}%", f"{pct_carb}%", f"{pct_prot}%", ""))
    print(datestr)
    print()
    print(tabulate.tabulate(table, headers=table_headers))

def choose_food():
    names = list(meta_foods.keys()) + list(foods.keys())
    for i, name in enumerate(names):
        print(f"{i + 1}. {name}")
    while True:
        index = input("> ")
        try:
            index = int(index)
        except ValueError:
            print("Invalid input. Retry again.")
            continue
        if not 0 < index <= len(names):
            print("Invalid item selected. Retry again.")
            continue
        break
    item = names[index - 1]
    print(f"Selected '{item}'")
    if item in meta_foods:
        add_meta(item)
    elif item in foods:
        amount = get_amount(item)
        add_food(item, amount, None)

def estimatoor(food, amount):
    if food in foods:
        food_estimatoor(food, amount)
    elif food in meta_foods:
        total_fat, total_carb, total_protein, total_calorie = 0, 0, 0, 0
        for food, amount in meta_foods[food].items():
            fat, carb, prot, cal = food_estimatoor(food, amount)
            total_fat += fat
            total_carb += carb
            total_protein += prot
            total_calorie += cal
        print()
        print(f"Total:")
        print(f"    Fat:        {total_fat}")
        print(f"    Carb:       {total_carb}")
        print(f"    Protein:    {total_protein}")
        print(f"    Calories:   {total_calorie}")

def food_estimatoor(food, amount):
    fat, carb, protein = foods[food]
    mult = amount / 100
    fat = round(mult*fat)
    carb = round(mult*carb)
    protein = round(mult*protein)
    calorie = round(9*fat + 4*carb + 4*protein)
    print(f"{food} ({amount}g):")
    print(f"    Fat:        {fat}")
    print(f"    Carb:       {carb}")
    print(f"    Protein:    {protein}")
    print(f"    Calories:   {calorie}")

    return fat, carb, protein, calorie

def main(argv):
    if len(argv) == 1:
        datestr = today_datestr()
        show_summary(datestr)
    elif len(argv) == 2:
        command = argv[1]
        #if command in meta_foods:
        #    add_meta(command)
        #    datestr = today_datestr()
        #    show_summary(datestr)
        if command in foods:
            amount = get_amount(command)
            add_food(command, amount, None)
            datestr = today_datestr()
            show_summary(datestr)
        elif command == "show":
            datestr = today_datestr()
            show_summary(datestr)
        elif command == "list":
            names = list(meta_foods.keys()) + list(foods.keys())
            for name in names:
                print(name)
        elif command == "edit":
            datestr = today_datestr()
            filename = date_filename(datestr)
            os.system(f"nvim {filename}")
    elif len(argv) == 3:
        command = argv[1]
        assert command == "show"
        datestr = argv[2]
        show_summary(datestr)
    elif len(argv) == 4:
        command = argv[1]
        assert command == "est"
        food = argv[2]
        amount = argv[3]
        try:
            amount = int(amount)
        except ValueError:
            print("Invalid amount. Quitting.")
            return -1
        estimatoor(food, amount)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

