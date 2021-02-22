import os
import hashlib
import csv
import traceback


def archive(path, file_list, archive_path):
    for file in file_list:
        res = input(file + " was processed would you like to archive it? (y/n): ")
        if res == 'y':
            full_name = path + '/' + file
            archive_name = archive_path + '/' + file
            os.rename(full_name, archive_name)


def gen_hash(path, file):
    block_size = 65536
    hashed = hashlib.sha1()
    fullname = path + '/' + file
    with open(fullname, "rb") as open_file:
        buf = open_file.read(block_size)
        while len(buf) > 0:
            hashed.update(buf)
            buf = open_file.read(block_size)
    return hashed.hexdigest()


def read_config(file='config', path='.') -> dict:
    try:
        output = {}
        full_name = path + '/' + file
        with open(full_name, newline='\n') as file:
            for line in file:
                items = line.split()
                output[items[0]] = items[1]
        return output
    except Exception:
        traceback.print_exc()


def write_file(file_list, hash_list, file, dev):
    try:
        with open(file, 'w', newline='\n') as csv_file:
            writer = csv.writer(csv_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in range(len(file_list)):
                if dev:
                    writer.writerow([file_list[i]] + [hash_list[i] + "dev"])
    except ValueError:
        traceback.print_exc()


def read_file(file='check.csv') -> list:
    try:
        output = []
        files = os.listdir(".")
        print(files)
        with open(file, newline='\n') as csv_file:
            reader = csv.reader(csv_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                output.append(row)
        return output
    except ValueError:
        traceback.print_exc()
