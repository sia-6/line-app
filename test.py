item_name = {
    "D": "Daily necessities",
    "F": "Food",
    "E": "Eating out",
    "T": "Transportation expenses"
}
i = "D"

s = [x for x in item_name.values()]
try:
    item_name[i]
    print("hello")
except:
    print("error")
