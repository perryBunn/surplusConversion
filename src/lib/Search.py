import sqlite3


def search_parse(args: [str], all: bool = False, other: bool = False, error: bool = False):
    keys = {
        "type": None,
        "make": None,
        "model": None,
        "serial": None,
        "inventory": None,
        "property": None,
        "location": None
    }
    tables = ["Surplus", "Other", "Errors"]
    for arg in args:
        temp = arg.split("=")
        keys[temp[0]] = temp[1]
    res = []
    if all:
        for i in range(3):
            res.append(search(type=keys["type"], make=keys["make"], model=keys["model"], serial=keys["serial"],
                              inventory=keys["inventory"], property=keys["property"], location=keys["location"],
                              table=tables[i]))
    if other:
        for i in range(2):
            res.append(search(type=keys["type"], make=keys["make"], model=keys["model"], serial=keys["serial"],
                              inventory=keys["inventory"], property=keys["property"], location=keys["location"],
                              table=tables[i]))
    if error:
        for i in range(0, 3, 2):
            res.append(search(type=keys["type"], make=keys["make"], model=keys["model"], serial=keys["serial"],
                              inventory=keys["inventory"], property=keys["property"], location=keys["location"],
                              table=tables[i]))
    return res


def search(type: str = None, make: str = None, model: str = None, serial: str = None, inventory: str = None,
           property: str = None, location: str = None, table: str = "Surplus"):
    conn = None
    conn = sqlite3.connect('Surplus.db')
    c = conn.cursor()

    tab = table
    find_type = "SELECT * FROM " + tab + " WHERE type=?"
    find_make = "SELECT * FROM " + tab + " WHERE make=?"
    find_model = "SELECT * FROM " + tab + " WHERE model=?"
    find_serial = "SELECT * FROM " + tab + " WHERE serialnumber=?"
    find_inventory = "SELECT * FROM " + tab + " WHERE inventorytag=?"
    find_property_control = "SELECT * FROM " + tab + " WHERE propertycontrol=?"
    find_location = "SELECT * FROM " + tab + " WHERE location=?"

    searchable = [type, make, model, serial, inventory, property, location]
    key_dict = {
        type: find_type,
        make: find_make,
        model: find_model,
        serial: find_serial,
        inventory: find_inventory,
        property: find_property_control,
        location: find_location
    }

    params = 0
    query = ""

    for key in searchable:
        if key is not None:
            if params > 0:
                query += " INTERSECT " + key_dict[key]
                query = query.replace("?", f"'{key}'", 1)
                params += 1
            else:
                query += key_dict[key]
                query = query.replace("?", f"'{key}'", 1)
                params += 1

    c.execute(query)
    rows = c.fetchall()
    if rows.__len__() > 1:
        print("Found multiple: ")
    for row in rows:
        print(row)
    return rows
