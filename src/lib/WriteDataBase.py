import sqlite3
import pandas as pd

from lib.Add import insert


def write_db(data: pd.DataFrame, dev: bool):
    """
    Everything must have a Serial number.
    As iterating through the dataframe search the table for the serial number is its not found then add it.
    """

    conn = None
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
            insert(cursor=c, item=item, err=None)
        except sqlite3.Error as e:
            print(item)
            print("Adding to errored...")
            print(e)
            insert(c, item, e)

    conn.commit()
    conn.close()
