import pandas as pd
import os
import hashlib
import csv
import traceback


def write_file(file_list, hash_list):
    try:
        with open('check.csv', 'w', newline='\n') as csv_file:
            writer = csv.writer(csv_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in range(len(file_list)):
                writer.writerow([file_list[i]] + [hash_list[i]])
    except ValueError:
        traceback.print_exc()


def read_file():
    try:
        output = []
        with open('check.csv', newline='\n') as csv_file:
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


def convert_changed(path, files):
    # TODO: currently does not go through every page of the file, need to fix.
    merged = None
    for file in files:
        full_name = path + '/' + file
        data = pd.read_excel(io=full_name, header=0, engine='openpyxl', na_filter=False, parse_dates=True,
                             dtype={'Location': 'string'}, sheet_name=None)
        print(data)
        if type(data) is dict:
            keys = data.keys()
            temp = pd.DataFrame()
            for key in keys:
                if merged is None:
                    merged = data[key]
                else:
                    merged = pd.concat([merged, data[key]], axis=0, join='outer', ignore_index=False, keys=None,
                                       levels=None, names=None, verify_integrity=False, copy=True)
        elif merged is None:
            merged = data
        else:
            merged = pd.concat([merged, data], axis=0, join='outer', ignore_index=False, keys=None, levels=None,
                               names=None, verify_integrity=False, copy=True)
    merged.reset_index(drop=True, inplace=True)
    res = merged.replace(to_replace={'Type': r'^\s+$'}, value='NaN', regex=True,)
    res.drop(merged.columns[merged.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
    print(res)
    with pd.ExcelWriter('test.xlsx') as writer:
        res.to_excel(writer)
    print('Wrote excel file')


def archive_file(path, file_list, archive):
    for file in file_list:
        res = input(file + " was processed would you like to archive it? (y/n): ")
        if res == 'y':
            full_name = path + '/' + file
            archive_name = archive + '/' + file
            os.rename(full_name, archive_name)
        else:
            print(file, " was not moved.")


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

    obj = read_file()  # Reads in existing check file
    changed_files = []
    for row in obj:
        if not hash_list.__contains__(row[1]):
            print("File has changed. Updating %s..." % (row[0]))
            changed_files.append(row[0])
            # write_file(file_list, hash_list) # TODO: uncomment this line when not debugging.
    if changed_files.__len__() != 0:
        convert_changed(ingest_path, changed_files)
    archive_file(ingest_path, file_list, archive_path)


if __name__ == '__main__':
    main()
