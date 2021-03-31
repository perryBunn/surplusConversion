import os
import re
import numpy as np
import pandas as pd
import configparser

import toml

from lib.Support import archive, read_config, read_file, gen_hash, write_file
from lib.WriteDataBase import write_db


def convert_changed(path, files):
    config = toml.load('config.toml')
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
    write_db(res, dev=config['DEFAULT'].getboolean('dev'))
    print('Wrote to db')


# TODO: This file needs to be rearranged for readability.
def ingest(ingest_path="./ingest", archive_path="./archive", check_path='check.csv'):
    config = toml.load('config.toml')
    # Read directory 'ingest'
    # Get list of excel sheets
    files = os.listdir(ingest_path)  # TODO: This need to have a check to make sure that the path exist
    print(files)
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
    obj = read_file(check_path)  # Reads in existing check file
    changed_files = []
    for row in obj:
        if not hash_list.__contains__(row[1]) and file_list.__contains__(row[0]):
            print("File has changed. Updating %s..." % (row[0]))
            changed_files.append(row[0])
            write_file(file_list, hash_list, check_path, config['DEFAULT'].getboolean('dev'))
        if not file_list.__contains__(row[0]):
            changed_files.append(row[0])
    if changed_files.__len__() != 0:
        convert_changed(ingest_path, changed_files)
    if not config['DEFAULT']['noarchive']:
        archive(ingest_path, file_list, archive_path)
