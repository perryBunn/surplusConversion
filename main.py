import pandas as pd
import numpy as np
import os
import hashlib
import csv
import traceback
import sqlite3
import re

dev = False


def write_file(file_list, hash_list, file='check.csv'):
    try:
        with open(file, 'w', newline='\n') as csv_file:
            writer = csv.writer(csv_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in range(len(file_list)):
                writer.writerow([file_list[i]] + [hash_list[i]])
    except ValueError:
        traceback.print_exc()


def read_file(file='check.csv'):
    try:
        output = []
        with open(file, newline='\n') as csv_file:
            reader = csv.reader(csv_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                output.append(row)
        return output
    except ValueError:
        traceback.print_exc()


def hash(path, file):
    block_size = 65536
    hasher = hashlib.sha1()
    fullname = path + '/' + file
    with open(fullname, "rb") as open_file:
        buf = open_file.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = open_file.read(block_size)
    return hasher.hexdigest()


def insert_db(cursor, item: list, err: Exception):
    insert_data = "INSERT INTO Surplus (type, make, model, serialnumber, propertycontrol, location, notes, " \
                  "inventorytag, issuetrakcorrected) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    no_serial = "INSERT INTO Other (type, make, model, propertycontrol, location, notes, inventorytag, " \
                "issuetrakcorrected) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    insert_malform = "INSERT INTO Errors (type, make, model, serialnumber, propertycontrol, location, notes, " \
                     "inventorytag, issuetrakcorrected) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

    res = type(item[3])
    if err is None:
        print(err)
        if res == float:
            cursor.execute(no_serial, (item[0], item[1], item[2], item[4], item[5], item[6], item[7], item[8]))
        else:
            cursor.execute(insert_data, (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8]))
    else:
        print("Error", err)
        cursor.execute(insert_malform, (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8]))


def write_db(data: pd.DataFrame):
    """
    Everything must have a Serial number.
    As iterating through the dataframe search the table for the serial number is its not found then add it.
    """

    conn = None
    try:
        conn = sqlite3.connect('Surplus.db')
        c = conn.cursor()

        if dev:
            print('PURGE WITH HOLY HELLFIRE!')
            purge = "DELETE FROM Surplus"
            c.execute(purge)
            purge = "DELETE FROM Other"
            c.execute(purge)
            purge = "DELETE FROM Errors"
            c.execute(purge)
            conn.commit()

        find_serial = "SELECT * FROM Surplus WHERE serialnumber=?"

        clean = "DELETE FROM Other WHERE type IS '' "

        print("Adding Data")
        for index, row in data.iterrows():

            item = [row["Type"],
                    row["Make"],
                    str(row["Model"]),
                    row["serial_number"],
                    row["Property Control #"],
                    row["Location"],
                    row["Notes"],
                    row["Inventory Tag"],
                    row["Issuetrak Corrected"]]

            try:
                insert_db(c, item, None)
            except sqlite3.Error as e:
                print(item)
                print("Adding to errored...")
                print(e)
                insert_db(c, item, e)

        print("Cleaning DB")
        # TODO: https://stackoverflow.com/questions/1612267/move-sql-data-from-one-table-to-another
        c.execute(clean)
        conn.commit()
        conn.close()
    except sqlite3.Error as err:
        print(err)


def convert_changed(path, files):
    df1 = None
    for file in files:
        full_name = path + '/' + file
        data = pd.read_excel(io=full_name, header=0, engine='openpyxl', na_filter=False, parse_dates=True,
                             dtype={'Location': 'string'}, sheet_name=None)

        # If there are multiple sheets; merge sheets with df1
        patt = re.compile(r'(serial(number)?)|(s\/?n)')
        if type(data) is dict:
            keys = data.keys()
            for key in keys:
                for col in data[key].columns:
                    label = col.replace(' ', '').lower()
                    if re.match(patt, label):
                        data[key].rename(columns={col: "serial_number"}, inplace=True)

                if df1 is None:
                    df1 = data[key]
                else:
                    df1 = pd.concat([df1, data[key]], axis=0, join='outer', ignore_index=False, keys=None,
                                    levels=None, names=None, verify_integrity=False, copy=True)
        else:
            for col in data.columns:
                label = col.replace(' ', '').lower()
                if re.match(patt, label):
                    data.rename(columns={col: "serial_number"}, inplace=True)

            if df1 is None:  # If first iteration
                df1 = data
            else:  # If data is only one sheet then merge to df1
                df1 = pd.concat([df1, data], axis=0, join='outer', ignore_index=False, keys=None, levels=None,
                                names=None, verify_integrity=False, copy=True)

    df1.reset_index(drop=True, inplace=True)

    try:
        with pd.ExcelWriter('df1.xlsx') as writer:
            df1.to_excel(writer)
        print('Wrote excel file')
    except Exception as e:
        print(e)

    # Replace "" values with NaN
    res = df1.replace(r'^\s*$', np.NaN, regex=True)
    # Drop columns
    res.drop(df1.columns[df1.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
    res.drop(df1.columns[df1.columns.str.contains('First and Last', case=False)], axis=1, inplace=True)
    res.drop(df1.columns[df1.columns.str.contains('Date', case=False)], axis=1, inplace=True)

    try:
        with pd.ExcelWriter('res.xlsx') as writer:
            df1.to_excel(writer)
        print('Wrote excel file')
    except Exception as e:
        print(e)

    write_db(res)
    print('Wrote to db')


def archive_file(path, file_list, archive):
    for file in file_list:
        res = input(file + " was processed would you like to archive it? (y/n): ")
        if res == 'y':
            full_name = path + '/' + file
            archive_name = archive + '/' + file
            os.rename(full_name, archive_name)


def main(*args, ingest_path="./ingest", archive_path="./archive"):
    global dev
    # Read directory 'ingest'
    # Get list of excel sheets
    files = os.listdir(ingest_path)  # TODO: This need to have a check to make sure that the path exist
    hash_list = []
    file_list = []

    for arg in args:
        if arg == '--dev':
            dev = True

    for f in files:
        file_extension = f[-5:]
        if file_extension == ".xlsx":
            hashcode = hash(ingest_path, f)
            file_list.append(f)
            hash_list.append(hashcode)
            print(f, hashcode)
        else:
            print(f)
    # TODO: Need a case for there being not check file.
    obj = read_file()  # Reads in existing check file
    changed_files = []
    for row in obj:
        # TODO: What if hash_list has items not in obj?
        if not hash_list.__contains__(row[1]):
            print("File has changed. Updating %s..." % (row[0]))
            changed_files.append(row[0])
            # write_file(file_list, hash_list) # TODO: uncomment this line when not debugging.
    if changed_files.__len__() != 0:
        convert_changed(ingest_path, changed_files)
    # archive_file(ingest_path, file_list, archive_path)  # TODO: uncomment this line when not debugging.


if __name__ == '__main__':
    main("--dev")
