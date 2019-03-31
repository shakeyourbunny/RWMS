# RimWorld database handling stuff
import json
import os
import sys
from urllib.request import urlopen


# download most recent DB
def download_database(url, filename):
    print("loading current RWMS database.")
    if url == "":
        print("no database URL defined.")
        sys.exit(1)
    if filename == "":
        print("no filename to download defined.")
        sys.exit(1)

    try:
        with urlopen(url) as jsonurl:
            jsondata = jsonurl.read()
    except:
        print("could not open {}".format(url))
        sys.exit(1)
    jsonurl.close()

    try:
        with open(filename, 'wb') as dbfile:
            dbfile.write(jsondata)
    except:
        print("could not write database data to {}".format(filename))
        sys.exit(1)
    dbfile.close()


# load database to memory
def load_database(filename):
    db = dict()
    if not os.path.isfile(filename):
        print("RWMS database {} not readable or found!".format(filename))

    with open(filename, 'r', encoding='UTF-8') as dbfile:
        try:
            db = json.loads(dbfile.read())
        except:
            print("Could not load data from {}.".format(filename))
    dbfile.close()

    return db
