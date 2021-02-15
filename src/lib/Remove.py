from lib.Search import *


def remove(args: [str], interact: bool = True):
    items = search_parse(args, all=True)
    print("Items to Remove: ")
    queue = []
    for item in items:
        if not item == []:
            if type(item) is list:
                for i in item:
                    queue.append(i)
                    print(i)
            else:
                queue.append(item)
                print(item)
    res = ""
    if interact:
        print("Starting interactive removal...")
        for item in queue:
            print(item)
            res = input("Remove? (Y/n) ")
            if res.upper() == "Y":
                print("Deleting...")
            else:
                queue.pop(item)
    else:
        res = input("Remove? (Y/n) ")
        if res.upper() == "Y":
            print("Deleting...")
        else:
            return
