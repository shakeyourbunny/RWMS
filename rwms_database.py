# RimWorld database handling stuff
import json
import sys
from urllib.request import urlopen

import rimworld_configuration
import rwms_error

wait_on_error = rimworld_configuration.__load_value_from_config("waitforkeypress_on_error", True)

# download most recent DB
def download_database(url):
    print("loading current RWMS database.")
    if url == "":
        rwms_error.fatal_error("no database URL defined.", wait_on_error)
        sys.exit(1)

    try:
        with urlopen(url) as jsonurl:
            jsondata = jsonurl.read()
    except:
        rwms_error.fatal_error("could not open {}".format(url), wait_on_error)
        sys.exit(1)
    jsonurl.close()

    db = dict()
    if jsondata:
        try:
            db = json.loads(jsondata)
        except:
            rwms_error.fatal_error("Could not load data from RWMSDB repository.", wait_on_error)
            sys.exit(1)

    return db


# load category mappings to
def load_categories_mapping(url):
    categories = dict()

    if url == "":
        rwms_error.fatal_error("no categories URL given!", wait_on_error)
        sys.exit(1)

    try:
        with urlopen(url) as jsonurl:
            jsondata = jsonurl.read()
    except:
        rwms_error.fatal_error("could not open {}".format(url), wait_on_error)
        sys.exit(1)
    jsonurl.close()

    try:
        categories = json.loads(jsondata)
    except:
        rwms_error.fatal_error("error parsing loaded jsondata from categories URL.", wait_on_error)
        sys.exit(1)

    return categories
