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
            reader = csv.reader(csv_file, delimiter=' ',  quotechar='|', quoting=csv.QUOTE_MINIMAL)
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


def convert_changed(path, file):
    full_name = path + '/' + file
    data = pd.read_excel(io=full_name, header=0, engine='openpyxl', na_values='Na')
    print(data)
    # data.to_sql('assets', con=)


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
    files = os.listdir(ingest_path)    # TODO: This need to have a check to make sure that the path exist
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
    for row in obj:
        if not hash_list.__contains__(row[1]):
            print("File has changed. Updating %s..." % (row[0]))
            convert_changed(ingest_path, row[0])
            write_file(file_list, hash_list)

    archive_file(ingest_path, file_list, archive_path)


if __name__ == '__main__':
    main()
