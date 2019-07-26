# RimWorld database handling stuff
import json
import sys
import os
from urllib.request import urlopen

import RWMS.configuration
import RWMS.error

wait_on_error = RWMS.configuration.load_value("rwms", "waitforkeypress_on_error", True)


# download most recent DB
def download_database(url):
    print("loading database.")
    if url == "":
        RWMS.error.fatal_error("no database URL defined.", wait_on_error)
        sys.exit(1)

    try:
        with urlopen(url) as jsonurl:
            jsondata = jsonurl.read()
    except:
        RWMS.error.fatal_error("could not open {}".format(url), wait_on_error)
        sys.exit(1)
    jsonurl.close()

    db = dict()
    if jsondata:
        try:
            db = json.loads(jsondata.decode("utf-8"))
            #python 3.6 and above can decode bytes objects automatically, python 3.5 and below cannot.
        except:
            RWMS.error.fatal_error("Could not load data from RWMSDB repository.", wait_on_error)
            sys.exit(1)

    return db


# load category mappings to
def load_categories_mapping(url):
    categories = dict()

    if url == "":
        RWMS.error.fatal_error("no categories URL given!", wait_on_error)
        sys.exit(1)

    try:
        with urlopen(url) as jsonurl:
            jsondata = jsonurl.read()
    except:
        RWMS.error.fatal_error("could not open {}".format(url), wait_on_error)
        sys.exit(1)
    jsonurl.close()

    try:
        categories = json.loads(jsondata.decode("utf-8"))
    except:
        RWMS.error.fatal_error("error parsing loaded jsondata from categories URL.", wait_on_error)
        sys.exit(1)

    return categories
