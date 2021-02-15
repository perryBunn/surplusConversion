def insert(cursor, item: list, err: Exception):
    insert_data = "INSERT INTO Surplus (type, make, model, serialnumber, propertycontrol, location, notes, " \
                  "inventorytag, issuetrakcorrected) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    no_serial = "INSERT INTO Other (type, make, model, propertycontrol, location, notes, inventorytag, " \
                "issuetrakcorrected) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    insert_malformed = "INSERT INTO Errors (type, make, model, serialnumber, propertycontrol, location, notes, " \
                       "inventorytag, issuetrakcorrected) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

    res = type(item[3])
    if err is None:
        if res == float:
            cursor.execute(no_serial, (item[0], item[1], item[2], item[4], item[5], item[6], item[7], item[8]))
        else:
            cursor.execute(insert_data,
                           (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8]))
    else:
        print("Error", err)
        cursor.execute(insert_malformed,
                       (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8]))
