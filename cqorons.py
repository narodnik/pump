import json
import os, sys
import tabulate
from datetime import datetime

meta_foods = {
    "lunch": {
        "canned-tuna": 150,
        "bread": 100,
        "egg": 150,
        "oil": 5,
    },
    "biglunch": {
        "canned-tuna": 150,
        "bread": 200,
        "egg": 150,
        "oil": 5,
    },
    "dinner": {
        "chicken-breast": 400,
        "sweet-potato": 400,
        # 1/20th litre = 50ml
        "juice": 50,
    }
}

# fat, carb, protein
foods = {
    "canned-tuna":  (1,     0,      22),
    "bread":        (5.5,   46,     10),
    "egg":          (11,    1,      13),
    "oil":          (90,    0,      0),
    "chicken-breast": (1.2, 0,      24),
    "sweet-potato": (0,     20,     1.6),
    "potato":       (0,     17,     2),
    "juice":        (0,     10,     0),
    "choc":         (31,    61,     5),
    "melon":        (0,     9,      0),
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
    mult = amount / 100
    append_data({
        "food": food,
        "amount": amount,
        "fat": fat * mult,
        "carb": carb * mult,
        "protein": protein * mult,
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
        fat = item["fat"]
        carb = item["carb"]
        protein = item["protein"]
        calorie = 9*fat + 4*carb + 4*protein

        total_fat += fat
        total_carb += carb
        total_protein += protein

        table.append((food, amount, round(fat), round(carb),
                      round(protein), round(calorie)))

    total_calorie = round(9*total_fat + 4*total_carb + 4*total_protein)
    table.append(("", "", "", "", "", ""))
    table.append(("Total:", "",
                  round(total_fat), round(total_carb),
                  round(total_protein), round(total_calorie)))
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

def main(argv):
    if len(argv) == 2:
        command = argv[1]
        if command in meta_foods:
            add_meta(command)
        elif command in foods:
            amount = get_amount(command)
            add_food(command, amount, None)
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
    else:
        choose_food()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

