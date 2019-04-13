## RimWorld ModSorter update module
##
## checks repo for newly commited versions and (in some point in the future) an inplace upgrade

import sys
from urllib.request import urlopen

version_url = "https://raw.githubusercontent.com/shakeyourbunny/RWMS/master/VERSION"


def __load_version_from_repo():
    try:
        data = str(urlopen(version_url).readline())

    except:
        print("** updatecheck: could not load update URL.")
        sys.exit(1)

    return data


def is_update_available(currentversion):
    if currentversion == "":
        return False

    if __load_version_from_repo() == currentversion:
        return False
    else:
        return True


# debug
if __name__ == '__main__':
    print(__load_version_from_repo())
