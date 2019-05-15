### RimWorld ModSorter error handling
#
# encapsulates error handling
import sys


def fatal_error(message, wait=True):
    print("*** fatal error: {}".format(message))
    print("")
    if wait:
        input("Press ENTER to terminate the program.")
    sys.exit(1)


if __name__ == '__main__':
    pass
