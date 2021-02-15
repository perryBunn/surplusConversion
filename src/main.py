import argparse
import os
import re
import numpy as np
import pandas as pd

from lib.Search import search_parse
from lib.Support import archive, read_config, read_file, gen_hash, write_file
from lib.Remove import remove
from lib.WriteDataBase import write_db
from lib.Namespace import Namespace
from src.GUI import GUI

dev = False
no_archive: False


def convert_changed(path, files):
    df1 = None
    for file in files:
        full_name = path + '/' + file
        data = pd.read_excel(io=full_name, header=0, engine='openpyxl', na_filter=False, parse_dates=True,
                             dtype={'Location': 'string'}, sheet_name=None)
        # noinspection RegExpRedundantEscape
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
        with pd.ExcelWriter('../df1.xlsx') as writer:
            df1.to_excel(writer)
        print('Wrote excel file')
    except Exception as e:
        print(e)
    # Replace "" values with NaN
    res = df1.replace(r'^\s*$', np.NaN, regex=True)
    # res = res.replace(r'^n/a$', np.NaN, regex=True)
    # Drop columns
    res.drop(df1.columns[df1.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
    res.drop(df1.columns[df1.columns.str.contains('First and Last', case=False)], axis=1, inplace=True)
    res.drop(df1.columns[df1.columns.str.contains('Date', case=False)], axis=1, inplace=True)
    try:
        with pd.ExcelWriter('../res.xlsx') as writer:
            df1.to_excel(writer)
        print('Wrote excel file')
    except Exception as e:
        print(e)
    write_db(res, dev=dev)
    print('Wrote to db')


def main(ingest_path="./ingest", archive_path="./archive", check_path='check.csv'):
    global no_archive
    global dev
    # Read directory 'ingest'
    # Get list of excel sheets
    files = os.listdir(ingest_path)  # TODO: This need to have a check to make sure that the path exist
    hash_list = []
    file_list = []

    for file in files:
        file_extension = file[-5:]
        if file_extension == ".xlsx":
            hashcode = gen_hash(ingest_path, file)
            file_list.append(file)
            hash_list.append(hashcode)
            print(file, hashcode)
    # TODO: Need a case for there being not check file.
    obj = read_file()  # Reads in existing check file
    changed_files = []
    for row in obj:
        if not hash_list.__contains__(row[1]) and file_list.__contains__(row[0]):
            print("File has changed. Updating %s..." % (row[0]))
            changed_files.append(row[0])
            write_file(file_list, hash_list, check_path, dev)
        if not file_list.__contains__(row[0]):
            changed_files.append(row[0])
    if changed_files.__len__() != 0:
        convert_changed(ingest_path, changed_files)
    if not no_archive:
        archive(ingest_path, file_list, archive_path)


c = Namespace()
parser = argparse.ArgumentParser(allow_abbrev=False)

parser.add_argument("--dev", action='store_true', help="Will do special dev stuff")
parser.add_argument("--version", action='store_true', help="Returns the package version")
parser.add_argument("--nogui", action='store_true', help="Will not start the GUI")
# Adds a new sheet
parser.add_argument("--add", action='store_true', help="Adds new Excel files from the ingest")
parser.add_argument("ingest", nargs="?", default="./ingest", help="Sets the ingest path")
parser.add_argument("archive", nargs="?", default="./archive", help="Sets the archive path")
# Defaults to just Surplus
parser.add_argument("--search", nargs="*", help="Will search Surplus table for an asset")
# Searches all tables
parser.add_argument("-A", action='store_true', help="Will search all tables")
# Searches Surplus and Other
parser.add_argument("-o", action='store_true', help="Will search the Other table")
# Searches Surplus and Errors
parser.add_argument("-E", action='store_true', help="Will search the Error table")
parser.add_argument("--remove", nargs="*", help="Will remove an asset from the database")
parser.add_argument("--get_errs", help="Will print the assets in the Errors table")
parser.add_argument("--no_archive", action='store_true')

config = read_config(file='config')

parser.parse_args(namespace=c)
if c.version:
    print("Version:", config["version"])
    exit()
if c.dev:
    dev = True
    print("Developer mode enabled.")
if not c.nogui:
    GUI.gui()
else:
    if c.no_archive:
        no_archive = True
    if c.A:
        A = True
    if c.o:
        o = True
    if c.E:
        E = True
    if c.add:
        main(c.ingest, c.archive)
        exit()
    if c.search:
        search_parse(c.search, c.A, c.o, c.E)
        exit()
    if c.remove:
        remove(c.remove)
        exit()
    if c.get_errs:
        print("Not implemented")
        exit()
    raise ValueError("No arguments were passed")
