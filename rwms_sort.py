#!/usr/bin/env python3
# RimWorld Module Sorter
import collections
import json
import os
import re
import shutil
import sys
import textwrap
import time
import webbrowser
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
from operator import itemgetter
from urllib.request import urlopen

from bs4 import BeautifulSoup

import RWMS.configuration
import RWMS.database
import RWMS.error
import RWMS.issue_mgmt
import RWMS.update

# ##################################################################################
# some basic initialization
VERSION = "0.94.7"

twx, twy = shutil.get_terminal_size()

parser = ArgumentParser()

# configuration overrides
parser.add_argument("--disable-steam", action="store_true", help="force disable steam detection")
parser.add_argument("--dont-remove-unknown-mods", action="store_true", help="do not remove unknown mods")

# misc options
parser.add_argument("--contributors", action="store_true", help="display all contributors to RWMS(DB)")
parser.add_argument("--dump-configuration", action="store_true",
                    help="displays the current configuration RWMS is thinking of")
parser.add_argument("--dump-database", action="store_true", help="display the full mod database as json")
parser.add_argument("--dump-database-scores", action="store_true", help="display a sorted mapping from mod name to sort score as json")

parser.add_argument("--reset-to-core", action="store_true", help="reset mod list to Core only")
args = parser.parse_args()

banner = "** RWMS {} by shakeyourbunny ".format(VERSION)
print("{:*<{tw}}".format(banner, tw=twx))
print("bugs: https://github.com/shakeyourbunny/RWMS/issues")
print("database updates: visit https://github.com/shakeyourbunny/RWMSDB/issues")
print("")

updatecheck = RWMS.configuration.load_value("rwms", "updatecheck", True)
openbrowser = RWMS.configuration.load_value("rwms", "openbrowser", True)
wait_on_error = RWMS.configuration.load_value("rwms", "waitforkeypress_on_error", True)
wait_on_exit = RWMS.configuration.load_value("rwms", "waitforkeypress_on_exit", True)
disablesteam = RWMS.configuration.load_value("rwms", "disablesteam", True)
dontremoveunknown = RWMS.configuration.load_value("rwms", "dontremoveunknown", False)

def go_exit(exit_code):
    if wait_on_exit:
        print("")
        input("Press ENTER to end program.")
    sys.exit(exit_code)

# command line switches, override configuration file
if args.disable_steam:
    disablesteam = True

if args.dont_remove_unknown_mods:
    dontremoveunknown = True

if args.dump_configuration:
    RWMS.configuration.__dump_configuration()
    go_exit(0)

if updatecheck:
    if RWMS.update.is_update_available(VERSION):
        print("*** Update available, new version is {} ***".format(RWMS.update.__load_version_from_repo()))
        print("")
        print("Release: https://github.com/shakeyourbunny/RWMS/releases")
        print("")
        if openbrowser:
            webbrowser.open_new("https://www.github.com/shakeyourbunny/RWMS/releases")

if RWMS.configuration.detect_rimworld() == "":
    RWMS.error.fatal_error("no valid RimWorld installation detected!", wait_on_error)
    sys.exit(1)

categories_url = 'https://raw.githubusercontent.com/shakeyourbunny/RWMSDB/master/rwms_db_categories.json'
database_url = "https://raw.githubusercontent.com/shakeyourbunny/RWMSDB/master/rwmsdb.json"


#####################################################################################################################
# functions - cleanup_garbage_name(garbagename)
def cleanup_garbage_name(garbagename):
    clean = garbagename
    regex = re.compile(
        r"(v|V|)\d+\.\d+(\.\d+|)([a-z]|)|\[(1.0|(A|B)\d+)\]|\((1.0|(A|B)\d+)\)|(for |R|)(1.0|(A|B)\d+)|\.1(8|9)")
    clean = re.sub(regex, "", clean)
    clean = re.sub(regex, "", clean)
    clean = clean.replace(" - ", ": ").replace(" : ", ": ")
    #
    clean = clean.replace("  ", " ")
    clean = " ".join(clean.split()).strip()

    # cleanup ruined names
    clean = clean.replace("()", "")
    clean = clean.replace("[]", "")

    # special cases
    clean = clean.replace("(v. )", "")  # Sora's RimFantasy: Brutal Start (v. )
    if clean.endswith(" Ver"):
        clean = clean.replace(" Ver", "")  # Starship Troopers Arachnids Ver
    if clean.endswith(" %"):
        clean = clean.replace(" %", "")  # Tilled Soil (Rebalanced): %
    if clean.find("[ "):
        clean = clean.replace("[ ", "[")  # Additional Traits [ Update]
    if clean.find("( & b19)"):
        clean = clean.replace("( & b19)", "")  # Barky's Caravan Dogs ( & b19)
    if clean.find("[19]"):
        clean = clean.replace("[19]", "")  # Sailor Scouts Hair [19]
    if clean.find("[/] Version"):
        clean = clean.replace("[/] Version", "")  # Fueled Smelter [/] Version

    if clean.endswith(":"):
        clean = clean[:-1]
    if clean.startswith(": "):
        clean = clean[2:]  # : ACP: More Floors Wool Patch
    if clean.startswith("-"):
        clean = clean[1:]  # -FuelBurning

    clean = clean.strip()

    return clean


######################################################################################################################
# functions - read in mod data
#
# db_score   = FULL dict of mod to score, where score is the mod's category's score + (index of mod / # total mods), for stable sorting
# basedir    = mod base directory
# modsource  = type of mod installation
#
def load_mod_data(db_score, basedir, modsource):
    mod_details = dict()
    folderlist = os.listdir(basedir)
    name = str()
    for moddirs in folderlist:
        aboutxml = basedir + '/' + moddirs + "/About/About.xml"
        if os.path.isfile(aboutxml):
            try:
                xml = ET.parse(aboutxml)
                name = xml.find('name').text
            except ET.ParseError:
                print("Mod ID is '{}'".format(moddirs))
                print("** error: malformed XML in {}".format(aboutxml))
                # print("Line {}, Offset {}".format(pe.lineno, pe.offset))
                print("")
                print("Please contact mod author for clarification.")
                if RWMS.configuration.detect_rimworld_steam():
                    workshopurl = "https://steamcommunity.com/sharedfiles/filedetails/?id=" + moddirs
                    print("(trying to workaround by loading steam workshop page {})".format(workshopurl))
                    try:
                        name = str(BeautifulSoup(urlopen(workshopurl), "html.parser").title.string)
                        if 'Steam Community :: Error' in name:
                            RWMS.error.fatal_error("Could not find a matching mod on the workshop.", wait_on_error)
                            sys.exit(1)
                    except:
                        print("Could not open workshop page. sorry.")
                    name = name.replace('Steam Workshop :: ', '')
                    print("Matching mod ID '{}' with '{}'".format(moddirs, name))
                    print("")
                else:
                    RWMS.error.fatal_error("(cannot do a workaround, no steam installation)", wait_on_error)
                    sys.exit(1)

            # cleanup name stuff for version garbage
            name = cleanup_garbage_name(name)

            if name in db_score:
                try:
                    score = db_score[name]
                except:
                    print("FIXME: mod '{}' has an unknown category '{}'. stop.".format(name, db["db"][name]))
                    RWMS.error.fatal_error("please report this error to the database maintainer.", wait_on_error)
                    sys.exit(1)

                # print("mod {} has a score of {}".format(name, score))
                try:
                    mod_entry = (moddirs, float(score), name, modsource)

                except KeyError:
                    RWMS.error.fatal_error(
                        "could not construct dictionary entry for mod {}, score {}".format(name, score), wait_on_error)
                    sys.exit(1)
            else:
                # print("mod '{}' is not in database, adding to unknown list.".format(name))
                mod_entry = (moddirs, None, name, modsource)

            mod_details[moddirs] = mod_entry
        else:
            print("could not find metadata for item " + moddirs + " (skipping, is probably a scenario)!")
            name = ""
    return mod_details


######################################################################################################################
# real start of the script

# load scoring mapping dict
cats = RWMS.database.load_categories_mapping(categories_url)
if not cats:
    RWMS.error.fatal_error("Could not load properly categories.", wait_on_error)
    sys.exit(1)

# preload all needed data
# categories
database = RWMS.database.download_database(database_url)
if not database:
    RWMS.error.fatal_error("Error loading scoring database {}.".format(database_url), wait_on_error)
    sys.exit(1)
db = database['db']
db_len = len(db)

# if os.path.isfile("rwms_database.json"):
#     print("loading local database.")
#     with open("rwms_database.json", 'r', encoding='utf-8') as f:
#         local_database = json.load(f)
#     # merging the local and remote databases in this way to prioritize ordering in local database over remote database
#     # this allows custom local reordering of mods in the same category
#     db = local_database.get('db', {}).copy()
#     for k, v in database['db'].items():
#         db.setdefault(k, v)
#     db_len = len(db)
#     database = {
#         'contributor': database['contributor'],
#         'db': db,
#         'remote_db': database['db'],
#         'timestamp': database['timestamp'],
#         'version': database['version'],
#     }

print("")
print("Database (v{}, date: {}) successfully loaded.".format(database["version"],
                                                                                database["timestamp"]))
print("{} known mods, {} contributors.".format(db_len, len(database["contributor"])))
if args.dump_database:
    print(json.dumps(db, indent=4))
    go_exit(0)

# if len(sys.argv) > 1 and sys.argv[1] == "contributors":
if args.contributors:
    print("{:<30} {:<6}".format('Contributor', '# Mods'))
    d = sorted(database["contributor"].items(), key=itemgetter(1), reverse=True)
    for contributors in d:
        if contributors[1] >= 10:
            print("{:<30} {:>5}".format(contributors[0], contributors[1]))
    go_exit(0)
else:
    contributors = collections.Counter(database["contributor"])
    print("Top contributors: ", end='')
    for c in contributors.most_common(5):
        print("{} ({}), ".format(c[0], c[1]), end='')
    print("")

modsconfigfile = RWMS.configuration.modsconfigfile()
print("")
print("Loading and parsing ModsConfig.xml")
if not os.path.isfile(modsconfigfile):
    RWMS.error.fatal_error("could not find ModsConfig.xml; detected: '{}'".format(modsconfigfile), wait_on_error)
    sys.exit(1)
xml = ET.parse(modsconfigfile)
xml = xml.find('activeMods')
mods_enabled_list = [t.text for t in xml.findall('li')]
if not "Core" in mods_enabled_list:
    mods_enabled_list.append("Core")

# generate dict of mod to score, where score is the mod's category's score + (index of mod / # total mods), for stable sorting
db_score = {mod_cat[0]: cats[mod_cat[1]][0] + float(index) / db_len for (index, mod_cat) in enumerate(db.items())}
if args.dump_database_scores:
    print(json.dumps(dict(sorted(db_score.items(), key=itemgetter(1))), indent=4))
    go_exit(0)

# check auf unknown mods
print("Loading mod data.")
mod_data_workshop = dict()
mod_data_local = dict()

if not disablesteam:
    steamworkshopdir = RWMS.configuration.detect_steamworkshop_dir()
    if RWMS.configuration.detect_rimworld_steam() != "":
        if not os.path.isdir(steamworkshopdir):
            RWMS.error.fatal_error(
                     "steam workshop directory '{}' could not be found. please check your installation and / or configuration file.".format(
                         steamworkshopdir), wait_on_error)
            sys.exit(1)
        mod_data_workshop = load_mod_data(db_score, steamworkshopdir, "W")

localmoddir = RWMS.configuration.detect_localmods_dir()
if not os.path.isdir(localmoddir):
    RWMS.error.fatal_error(
             "local mod directory '{}' could not be found. please check your installation and / or configuration file.".format(
                 localmoddir), wait_on_error)
    sys.exit(1)
mod_data_local = load_mod_data(db_score, localmoddir, "L")

mod_data_full = {**mod_data_local, **mod_data_workshop}
mod_data_known = {}
mod_data_unknown = {}
for mods, mod_entry in mod_data_full.items():
    if mod_entry[1] is not None:
        mod_data_known[mods] = mod_entry
        # always include mods unrecognized in remote database
        if 'remote_db' in database and mod_entry[2] not in database['remote_db']:
            mod_data_unknown[mods] = mod_entry
    else:
        mod_data_unknown[mods] = mod_entry

mods_data_active = list()
mods_unknown_active = list()
for mods in mods_enabled_list:
    try:
        mods_data_active.append([mods, mod_data_known[mods][1]])

    except KeyError:
        # print("Unknown mod ID {}, deactivating it from mod list.".format(mods))
        mods_unknown_active.append(mods)

print("Sorting mods.")
newlist = sorted(mods_data_active, key=itemgetter(1))
print("")
print("{} subscribed mods, {} ({} known, {} unknown) enabled mods".format(len(mod_data_full), len(mods_enabled_list),
                                                                          len(mods_data_active) + 1, len(mods_unknown_active)))

if not os.path.isfile(modsconfigfile):
    RWMS.error.fatal_error("error accessing " + modsconfigfile, wait_on_error)
    sys.exit(1)
doc = ET.parse(modsconfigfile)
xml = doc.getroot()

try:
    rimworld_version = xml.find('version').text
except:
    try:
        rimworld_version = xml.find('buildNumber').text
    except:
        rimworld_version = "unknown"

xml = xml.find('activeMods')
for li in xml.findall('li'):
    xml.remove(li)
# ET.dump(doc)

now_time = time.strftime('%Y%m%d-%H%M', time.localtime(time.time()))

write_modsconfig = False

if args.reset_to_core:
    while True:
        data = input("Do you want to reset your mod list to Core only (y/n)? ")
        if data.lower() in ('y', 'n'):
            break
    if data.lower() == "y":
        print("Resetting your ModsConfig.xml to Core only!")
        xml_sorted = ET.SubElement(xml, 'li')
        xml_sorted.text = "Core"
        write_modsconfig = True

else:
    for mods in newlist:
        # print(mods)
        if mods[0] == "":
            print("skipping, empty?")
        else:
            xml_sorted = ET.SubElement(xml, 'li')
            xml_sorted.text = str(mods[0])
        # ET.dump(doc)

    if dontremoveunknown:
        print("Adding in unknown mods in the load order (at the bottom).")
        for mods in mods_unknown_active:
            if mods[0] == "":
                print("skipping, empty?")
            else:
                xml_sorted = ET.SubElement(xml, 'li')
                xml_sorted.text = str(mods)

    ### finish -- unknown mods handling
    if mod_data_unknown:
        print("")
        print("Processing unknown mods.")
        DB = dict()
        DB["version"] = 2

        unknown_meta = dict()
        unknown_meta["contributor"] = RWMS.issue_mgmt.get_github_user().split("@")[0]
        unknown_meta["mods_unknown"] = len(mod_data_unknown)
        unknown_meta["mods_known"] = len(mods_data_active) + 1
        unknown_meta["rimworld_version"] = rimworld_version
        unknown_meta["rwms_version"] = VERSION
        unknown_meta["os"] = sys.platform
        unknown_meta["time"] = str(time.ctime())
        DB["meta"] = unknown_meta

        unknown_diff = dict()
        for mod_entry in mod_data_unknown.values():
            if mod_entry[3] == "L":
                mod_loc = os.path.join("<RimWorld install directory>", "Mods", mod_entry[0]) # not printing actual path for security/privacy
            elif not disablesteam:
                mod_loc = "https://steamcommunity.com/sharedfiles/filedetails/?id={}".format(mod_entry[0])
            else:
                mod_loc = ""
            unknown_diff[mod_entry[2]] = ("not_categorized", mod_loc)
        DB["unknown"] = unknown_diff

        unknownfile = "rwms_unknown_mods_{}.json.txt".format(now_time)
        print("Writing unknown mods.")
        print("")
        with open(unknownfile, "w", encoding="UTF-8", newline="\n") as f:
            json.dump(DB, f, indent=True, sort_keys=True)
        f.close()

        if RWMS.issue_mgmt.is_github_configured():
            print("Creating a new issue on the RWMSDB issue tracker.")
            with open(unknownfile, 'r', encoding="UTF-8") as f:
                issuebody = f.read()
            f.close()
            RWMS.issue_mgmt.create_issue('unknown mods found by ' + RWMS.issue_mgmt.get_github_user(), issuebody)
        else:
            print(textwrap.fill("For the full list of unknown mods see the written data file in the current directory. " +
                                "You can either submit the data file manually on the RWMSDB issue tracker or on Steam / " +
                                "Ludeon forum thread. Thank you!", 78))
            print("")
            print("Data file name is {}".format(unknownfile))
            print("")

            while True:
                data = input("Do you want to open the RWMSDB issues web page in your default browser (y/n): ")
                if data.lower() in ('y', 'n'):
                    break
            if data.lower() == "y":
                print("Trying to open the default webbrowser for RWMSDB issues page.")
                print("")
                webbrowser.open_new("https://www.github.com/shakeyourbunny/RWMSDB/issues")

        if dontremoveunknown:
            print("Unknown mods will be written at the end of the mod list.")
        else:
            print("Unknown mods will be removed.")
    else:
        print("lucky, no unknown mods detected!")

    # ask for confirmation to write the ModsConfig.xml anyway
    while True:
        data = input("Do you REALLY want to write ModsConfig.xml (y/n): ")
        if data.lower() in ('y', 'n'):
            break
    if data.lower() == 'y':
        write_modsconfig = True

if write_modsconfig:
    # do backup
    backupfile = modsconfigfile + '.backup-{}'.format(now_time)
    shutil.copy(modsconfigfile, backupfile)
    print("Backed up ModsConfig.xml to {}.".format(backupfile))

    print("Writing new ModsConfig.xml.")
    modsconfigstr = ET.tostring(doc.getroot(), encoding='unicode')
    with open(modsconfigfile, "w", encoding='utf-8-sig', newline="\n") as f:
        # poor man's pretty print
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        modsconfigstr = modsconfigstr.replace('</li><li>', '</li>\n    <li>').replace('</li></activeMods>', '</li>\n  </activeMods>')
        f.write(modsconfigstr)
    print("Writing done.")
else:
    print("ModsConfig.xml was NOT modified.")

go_exit(0)
