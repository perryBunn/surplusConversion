import pandas as pd
import os
import hashlib
import csv
import traceback
import sqlite3
import re


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


def write_db(data: pd.DataFrame):
    # TODO: Need to iterate though the data and add it to the db if it hasn't been added already.
    """
    Everything must have a Serial number.
    As iterating through the dataframe search the table for the serial number is its not found then add it.
    """

    conn = None
    try:
        conn = sqlite3.connect('Surplus.db')
        c = conn.cursor()
        for index, row in data.iterrows():
            type: str = row["Type"]
            make: str = row["Make"]
            model: str = row["Model"]
            sn: str = row["serial_number"]
            pc = row["Property Control #"]
            location: str = row["Location"]
            notes: str = row["Notes"]
            inventory = row["Inventory Tag"]
            corrected: bool = row["IssueTrak Corrected"]
            insert_data = "INSERT INTO Surplus (type, make, model, serialnumber, propertycontrol, location, notes, " \
                          "inventorytag, issuetrakcorrected) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            # If serial number is already there then skip
            found = False
            find_date = "SELECT * FROM Surplus WHERE serialnumber=?"

            # TODO: If Serial number is empty then it will not add any other assets that also do not have serial numbers

            c.execute(find_date, (sn,))
            res = c.fetchall()
            if res.__len__() > 0:
                found = True
            print(found, sn)
            if found:
                continue
            else:
                c.execute(insert_data, (type, make, model, sn, pc, location, notes, inventory, corrected))
                conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)


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
                    print(label)
                    if re.match(patt, label):
                        print(col, "matched!")
                        data[key].rename(columns={col: "serial_number"}, inplace=True)

                if df1 is None:
                    df1 = data[key]
                else:
                    df1 = pd.concat([df1, data[key]], axis=0, join='outer', ignore_index=False, keys=None,
                                       levels=None, names=None, verify_integrity=False, copy=True)
        else:
            for col in data.columns:
                label = col.replace(' ', '').lower()
                print(label)
                if re.match(patt, label):
                    print(col, "matched!")
                    data.rename(columns={col: "serial_number"}, inplace=True)

            if df1 is None:  # If first iteration
                df1 = data
            else:  # If data is only one sheet then merge to df1
                df1 = pd.concat([df1, data], axis=0, join='outer', ignore_index=False, keys=None, levels=None,
                               names=None, verify_integrity=False, copy=True)

    df1.reset_index(drop=True, inplace=True)
    res = df1.replace(to_replace={'Type': ' '}, value=None, regex=True,)
    # Drop columns
    res.drop(df1.columns[df1.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
    res.drop(df1.columns[df1.columns.str.contains('First and Last', case=False)], axis=1, inplace=True)
    res.drop(df1.columns[df1.columns.str.contains('Date', case=False)], axis=1, inplace=True)

    print(res)
    with pd.ExcelWriter('test.xlsx') as writer:
        res.to_excel(writer)
    print('Wrote excel file')
    write_db(res)
    print('Wrote to db')


def archive_file(path, file_list, archive):
    for file in file_list:
        res = input(file + " was processed would you like to archive it? (y/n): ")
        if res == 'y':
            full_name = path + '/' + file
            archive_name = archive + '/' + file
            os.rename(full_name, archive_name)


def main(ingest_path="./ingest", archive_path="./archive"):
    # Read directory 'ingest'
    # Get list of excel sheets
    files = os.listdir(ingest_path)  # TODO: This need to have a check to make sure that the path exist
    hash_list = []
    file_list = []

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
        if not hash_list.__contains__(row[1]):
            print("File has changed. Updating %s..." % (row[0]))
            changed_files.append(row[0])
            # write_file(file_list, hash_list) # TODO: uncomment this line when not debugging.
    if changed_files.__len__() != 0:
        convert_changed(ingest_path, changed_files)
    # archive_file(ingest_path, file_list, archive_path)  # TODO: uncomment this line when not debugging.


if __name__ == '__main__':
    main()
