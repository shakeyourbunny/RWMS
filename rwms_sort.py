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
VERSION = "0.94.8"

twx, twy = shutil.get_terminal_size()

parser = ArgumentParser()

# configuration overrides
parser.add_argument("--disable-steam", action="store_true", help="force disable steam detection")
parser.add_argument("--dont-remove-unknown-mods", action="store_true", help="do not remove unknown mods")

# misc options
parser.add_argument("--contributors", action="store_true", help="display all contributors to RWMS(DB)")
parser.add_argument("--dump-configuration", action="store_true",
                    help="displays the current configuration RWMS is thinking of")

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


def wait_for_exit(exit_code):
    if wait_on_exit:
        print("")
        input("Press ENTER to end program.")

# command line switches, override configuration file
if args.disable_steam:
    disablesteam = True

if args.dont_remove_unknown_mods:
    dontremoveunknown = True

if args.dump_configuration:
    RWMS.configuration.__dump_configuration()
    wait_for_exit(0)

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
database_file = "rwms_database.json"

mod_unknown = list()


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
# cats       = categories
# db         = FULL db dict
# modsource  = type of mod installation
#
def load_mod_data(cats, db, basedir, modsource):
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
            name_old = name
            name = cleanup_garbage_name(name)

            if name in db["db"]:
                try:
                    score = cats[db["db"][name]][0]
                except:
                    print("FIXME: mod '{}' has an unknown category '{}'. stop.".format(name, db["db"][name]))
                    RWMS.error.fatal_error("please report this error to the database maintainer.", wait_on_error)
                    sys.exit(1)

                # print("mod {} has a score of {}".format(name, score))
                try:
                    mod_entry = [moddirs, float(score), name, modsource]

                except KeyError:
                    RWMS.error.fatal_error(
                        "could not construct dictionary entry for mod {}, score {}".format(name, score), wait_on_error)
                    sys.exit(1)
            else:
                # print("mod '{}' is not in database, adding to unknown list.".format(name))
                # mod_unknown.append(name)
                mod_unknown.append([name, moddirs])
                mod_entry = list()

            if mod_entry:
                mod_details[moddirs] = mod_entry
        else:
            print("could not find metadata for item " + moddirs + " (skipping, is probably a scenario)!")
            name = ""
    return mod_details


######################################################################################################################
# real start of the script

# load scoring mapping dict
cat = RWMS.database.load_categories_mapping(categories_url)
if not cat:
    RWMS.error.fatal_error("Could not load properly categories.", wait_on_error)
    sys.exit(1)

# preload all needed data
# categories
database = RWMS.database.download_database(database_url)
if not database:
    RWMS.error.fatal_error("Error loading scoring database {}.".format(database_file), wait_on_error)
    sys.exit(1)
else:
    print("")
    print("Database (v{}, date: {}) successfully loaded.".format(database["version"],
                                                                 database["timestamp"]))
    print("{} known mods, {} contributors.".format(len(database["db"]), len(database["contributor"])))

# if len(sys.argv) > 1 and sys.argv[1] == "contributors":
if args.contributors:
    print("{:<30} {:<6}".format('Contributor', '# Mods'))
    d = sorted(database["contributor"].items(), key=itemgetter(1), reverse=True)
    for contributors in d:
        if contributors[1] >= 10:
            print("{:<30} {:>5}".format(contributors[0], contributors[1]))
    wait_for_exit(0)
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

try:
    xml = ET.parse(modsconfigfile)
except:
    RWMS.error.fatal_error("could not parse XML from ModsConfig.xml.", wait_on_error)
    sys.exit(1)

xml = xml.find('activeMods')
mods_enabled_list = [t.text for t in xml.findall('li')]
if not "Core" in mods_enabled_list:
    mods_enabled_list.append("Core")

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
        mod_data_workshop = load_mod_data(cat, database, steamworkshopdir, "W")

localmoddir = RWMS.configuration.detect_localmods_dir()
if not os.path.isdir(localmoddir):
    RWMS.error.fatal_error(
             "local mod directory '{}' could not be found. please check your installation and / or configuration file.".format(
                 localmoddir), wait_on_error)
    sys.exit(1)
mod_data_local = load_mod_data(cat, database, localmoddir, "L")

mod_data_full = {**mod_data_local, **mod_data_workshop}

mods_data_active = list()
mods_data_active_unknown = list()
for mods in mods_enabled_list:
    try:
        mods_data_active.append([mods, mod_data_full[mods][1]])

    except KeyError:
        # print("Unknown mod ID {}, deactivating it from mod list.".format(mods))
        print("Unknown ACTIVE mod ID {} found..".format(mods))
        mods_data_active_unknown.append(mods)


print("Sorting mods.")
newlist = sorted(mods_data_active, key=itemgetter(1))
print("")
print("{} subscribed mods, {} ({} known, {} unknown) enabled mods".format(len(mod_data_full), len(mods_enabled_list),
                                                                          len(mods_data_active) + 1, len(mod_unknown)))
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

if args.reset_to_core:
    while True:
        data = input("Do you want to reset your mod list to Core only (y/n)? ")
        if data.lower() in ('y', 'n'):
            break
    if data.lower() == "y":
        print("Resetting your ModsConfig.xml to Core only!")

        # do backup
        now_time = time.strftime('%Y%m%d-%H%M', time.localtime(time.time()))
        shutil.copy(modsconfigfile, modsconfigfile + '.backup-{}'.format(now_time))

        xml_sorted = ET.SubElement(xml, 'li')
        xml_sorted.text = "Core"

        doc.write(modsconfigfile, encoding='UTF-8', xml_declaration='False')
        wait_for_exit(1)
    elif data.lower() == "n":
        wait_for_exit(0)

for mods in newlist:
    # print(mods)
    if mods[0] == "":
        print("skipping, empty?")
    else:
        xml_sorted = ET.SubElement(xml, 'li')
        xml_sorted.text = str(mods[0])
    # ET.dump(doc)

### finish -- unknown mods handling
write_modsconfig = False
if mod_unknown:
    print("")
    print("Processing unknown mods.")
    DB = dict()
    DB["version"] = 2

    unknown_meta = dict()
    unknown_meta["contributor"] = RWMS.issue_mgmt.get_github_user().split("@")[0]
    unknown_meta["mods_unknown"] = len(mod_unknown)
    unknown_meta["mods_known"] = len(mods_data_active) + 1
    unknown_meta["rimworld_version"] = rimworld_version
    unknown_meta["rwms_version"] = VERSION
    unknown_meta["os"] = sys.platform
    unknown_meta["time"] = str(time.ctime())
    DB["meta"] = unknown_meta

    if dontremoveunknown:
        print("Adding in unknown mods in the load order (at the bottom).")
        for mods in mods_data_active_unknown:
            print("Adding {}.".format(mods))
            # xml_sorted = ET.SubElement(xml, 'li')
            # xml_sorted.text = str(mods)

            xml_mod = ET.Element("li")
            xml_mod.text = str(mods)

            xml_activeMods = doc.find("activeMods")
            xml_activeMods.append(xml_mod)
    unknown_diff = dict()
    for mods in mod_unknown:
        if not disablesteam:
            workshop_url = "https://steamcommunity.com/sharedfiles/filedetails/?id={}".format(mods[1])
        else:
            workshop_url = ""
        unknown_diff[mods[0]] = ["not_categorized", workshop_url]
    DB["unknown"] = unknown_diff

    now_time = time.strftime('%Y%m%d-%H%M', time.localtime(time.time()))
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

    # ask for confirmation to write the ModsConfig.xml anyway
    while True:
        if dontremoveunknown:
            print("Unknown, ACTIVE mods will be written at the end of the mod list.")
        else:
            print("Unknown, ACTIVE mods will be removed.")

        data = input("Do you REALLY want to write ModsConfig.xml (y/n): ")
        if data.lower() in ('y', 'n'):
            break

    if data.lower() == 'y':
        write_modsconfig = True
else:
    print("lucky, no unknown mods detected!")
    write_modsconfig = True

if write_modsconfig:
    # do backup
    now_time = time.strftime('%Y%m%d-%H%M', time.localtime(time.time()))
    backupfile = modsconfigfile + ".backup-{}".format(now_time)
    shutil.copy(modsconfigfile, backupfile)
    print("Backed up ModsConfig.xml to {}.".format(backupfile))

    print("Writing new ModsConfig.xml.")
    # doc.write(modsconfigfile, encoding='UTF-8', xml_declaration='False')
    modsconfigstr = ET.tostring(doc.getroot(), encoding='unicode')
    with open(modsconfigfile, "w", encoding='UTF-8', newline="\n") as f:
        # poor man's pretty print
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        modsconfigstr = modsconfigstr.replace('</li><li>', '</li>\n    <li>').replace('</li></activeMods>',
                                                                                      '</li>\n  </activeMods>')
        f.write(modsconfigstr)
    f.close()
    print("Writing done.")
else:
    print("ModsConfig.xml was NOT modified.")

wait_for_exit(0)
