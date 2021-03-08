import argparse
import configparser
from lib.Search import search_parse
from lib.Support import read_config, write_config
from lib.Remove import remove
from ingest import ingest
from lib.Namespace import Namespace
from interface import menu

dev = False
no_archive: False


def main():
    c = Namespace()
    parser = argparse.ArgumentParser(allow_abbrev=False)

    parser.add_argument("--dev", action='store_true', help="Will do special dev stuff")
    parser.add_argument("--version", action='store_true', help="Returns the package version")
    parser.add_argument("--nogui", action='store_true', help="Will not start the interface")
    # Adds a new sheet
    parser.add_argument("--add", action='store_true', help="Adds new Excel files from the ingest")
    parser.add_argument("ingest", nargs="?", default="./ingest", help="Sets the ingest path")
    parser.add_argument("archive", nargs="?", default="./archive", help="Sets the archive path")
    parser.add_argument("check", nargs="?", default="./check.csv", help="Sets the check path")
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

    config = configparser.ConfigParser()
    config.read('../config.ini')

    parser.parse_args(namespace=c)
    if c.version:
        print(config)
        temp = config['DEFAULT']['version']
        print("Version:", temp)
        exit()
    if c.dev:
        config.dev = True
        write_config(config, path='.')
        print("Developer mode enabled.")
    if c.no_archive:
        config.no_archive = True
        write_config(config)
    if not c.nogui:
        menu.gui()
    else:
        if c.A:
            A = True
        if c.o:
            o = True
        if c.E:
            E = True
        if c.add:
            ingest(c.ingest, c.archive, c.check)
            exit()
        if c.search:
            search_parse(c.search, c.A, c.o, c.E)
            exit()
        if c.remove:
            remove(c.remove)
            exit()
        if c.get_errs:
            raise NotImplementedError
        raise ValueError("No action arguments were passed")


if __name__ == '__main__':
    main()
