#!/usr/bin/python
import json
import os, sys
import tabulate
from datetime import datetime

from cq_config import meta_foods

# fat, carb, protein
foods = {
    "canned-tuna":  (1,     0,      22),
    "smoked-salmon": (4,    0,      18),
    "bread":        (5.5,   46,     10),
    "egg":          (11,    1,      13),
    "oil":          (90,    0,      0),
    "chicken-breast": (1.2, 0,      24),
    "sweet-potato": (0,     20,     1.6),
    "potato":       (0,     17,     2),
    "juice":        (0,     10,     0),
    "choc":         (31,    61,     5),
    "melon":        (0,     9,      0),
    "oats":         (5.3,   56,     11),
    "oat-milk":     (2,     8.4,    0.8),
    "dates":        (0.5,   66,     2),
    "rice":         (0,     78,     8.6),
    "grapes":       (0,     17,     0),
    "beef-jerky":   (4,     16,     39),
    "kidney-beans": (1,     60,     24),
    "beef":         (15,    0,      26),
    "peach":        (0,     10,     1),
    "tuna":         (1.3,   0,      28),
    "sweet-corn":   (1.2,   19,     3.2),
    "popcorn":      (0.9,   80,     9),
    "tahini":       (52.8,   9,    25.5),
    "salt-choc":    (44,    33,     6.8),
    "black-currant":(0,     15,     1.4),
    "red-currant":  (0,     13,     1.4),
    "fig":          (0.3,   19.2,   0.8),
    "pear":         (0.14,  15.2,   0.36),
    "plum":         (0.3,   11.4,   0.7),
    "mushroom":     (0.1,   4.3,    2.5),
}

dirname = "calories"

def today_filename():
    now = datetime.now()
    # We only want the last 2 digits
    year = str(now.year)[2:]
    filename = "%s/calorie_%02d%02d%s.wkt" % (dirname, now.day, now.month, year)
    return filename

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

def show_summary():
    filename = today_filename()
    if not os.path.isfile(filename):
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
        show_summary()
    elif len(argv) == 2:
        command = argv[1]
        if command in meta_foods:
            add_meta(command)
            show_summary()
        elif command in foods:
            amount = get_amount(command)
            add_food(command, amount, None)
            show_summary()
        elif command == "show":
            show_summary()
        elif command == "list":
            names = list(meta_foods.keys()) + list(foods.keys())
            for name in names:
                print(name)
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

