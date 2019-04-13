#!/usr/bin/python3
# RimWorld Module Sorter
import collections
import json
import os
import shutil
import sys
import time
import xml.etree.ElementTree as ET
from operator import itemgetter
from urllib.request import urlopen

from bs4 import BeautifulSoup

import rimworld_configuration
import rwms_database
import rwms_error
import rwms_update


def errormsg(wait, msg):
    rwms_error.fatal_error(wait, msg)


####################################
# ##################################################################################
# some basic initialization
VERSION = "0.93"

print("*** RWMS {} by shakeyourbunny".format(VERSION))
print("visit https://gitlab.com/rwms/rwms/issues for reporting problems,")
print("visit https://gitlab.com/rwms/rwmsdb/issues for uploading potential unknown mods.")
print("   please use the generated .json file.")
print("")

updatecheck = rimworld_configuration.__load_value_from_config("updatecheck", True)
openbrowser_on_update = rimworld_configuration.__load_value_from_config("openbrowser_on_update", True)
wait_on_error = rimworld_configuration.__load_value_from_config("waitforkeypress_on_error", True)
wait_on_exit = rimworld_configuration.__load_value_from_config("waitforkeypress_on_exit", True)
disablesteam = rimworld_configuration.__load_value_from_config("disablesteam", True)

if updatecheck:
    if rwms_update.is_update_available(VERSION):
        print("*** Update available, new version is {} ***".format(rwms_update.__load_version_from_repo()))
        print("")
        print("Release: https://gitlab.com/rwms/rwms/tags")
        print("Windows:  https://my.pcloud.com/publink/show?code=kZMpDE7Z6AR7dk8n8ibLB8EIhSPYU51E7xhX")
        print("")
    # time.sleep(1)

if rimworld_configuration.__detect_rimworld() == "":
    print("no valid RimWorld installation detected!")
    sys.exit(1)

categories_url = 'https://gitlab.com/rwms/rwmsdb/raw/master/rwms_db_categories.json'
database_url = "https://gitlab.com/rwms/rwmsdb/raw/master/rwmsdb.json"
database_file = "rwms_database.json"

mod_unknown = list()

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
            except ET.ParseError as pe:
                print("Mod ID is '{}'".format(moddirs))
                print("** error: malformed XML in {}".format(aboutxml))
                # print("Line {}, Offset {}".format(pe.lineno, pe.offset))
                print("")
                print("Please contact mod author for clarification.")
                if rimworld_configuration.__detect_rimworld_steam():
                    workshopurl = "https://steamcommunity.com/sharedfiles/filedetails/?id=" + moddirs
                    print("(trying to workaround by loading steamworkshop page {})".format(workshopurl))
                    try:
                        name = str(BeautifulSoup(urlopen(workshopurl), "html.parser").title.string)
                        if 'Steam Community :: Error' in name:
                            errormsg(wait_on_error, "Could not find a matching mod on the workshop.")
                            sys.exit(1)
                    except:
                        print("Could not open workshop page. sorry.")
                    name = name.replace('Steam Workshop :: ', '')
                    print("Matching mod ID '{}' with '{}'".format(moddirs, name))
                    print("")
                else:
                    errormsg(wait_on_error, "(cannot do a workaround, no steam installation)")
                    sys.exit(1)

            if name in db["db"]:
                try:
                    score = cats[db["db"][name]][0]
                except:
                    print("FIXME: mod '{}' has an unknown category '{}'. stop.".format(name, db["db"][name]))
                    errormsg(wait_on_error, "please report this error to the database maintainer.")
                    sys.exit(1)

                # print("mod {} has a score of {}".format(name, score))
                try:
                    mod_entry = [moddirs, float(score), name, modsource]

                except KeyError:
                    errormsg(wait_on_error,
                             "could not construct dictionary entry for mod {}, score {}".format(name, score))
                    sys.exit(1)
            else:
                # print("mod {} is not in database, adding to unknown list.".format(name))
                mod_unknown.append(name)
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
cat = rwms_database.load_categories_mapping(categories_url)
if not cat:
    errormsg(wait_on_error, "Could not load properly categories.")
    sys.exit(1)

# preload all needed data
# categories
rwms_database.download_database(database_url, database_file)
database = rwms_database.load_database(database_file)
if not database:
    errormsg(wait_on_error, "Error loading scoring database {}.".format(database_file))
    sys.exit(1)
else:
    print("")
    print("Database (structure v{}, last update {}) successfully loaded.".format(database["version"],
                                                                                 database["timestamp"]))
    print("{} known mods, {} contributors.".format(len(database["db"]), len(database["contributor"])))
    contributors = collections.Counter(database["contributor"])
    print("Top contributors: ", end='')
    for c in contributors.most_common(5):
        print("{} ({}), ".format(c[0], c[1]), end='')
    print("")
    print("")
time.sleep(3)

modsconfigfile = rimworld_configuration.get_modsconfigfile()
print("Loading and parsing ModsConfig.xml")
if not os.path.isfile(modsconfigfile):
    errormsg(wait_on_error, "could not find ModsConfig.xml; detected: '{}'".format(modsconfigfile))
    sys.exit(1)
xml = ET.parse(modsconfigfile)
xml = xml.find('activeMods')
mods_enabled_list = [t.text for t in xml.findall('li')]
if not "Core" in mods_enabled_list:
    mods_enabled_list.append("Core")

# check auf unknown mods
time.sleep(1)
print("")
print("Loading mod data.")
mod_data_workshop = dict()
mod_data_local = dict()

if not disablesteam:
    steamworkshopdir = rimworld_configuration.get_mods_steamworkshop_dir()
    if rimworld_configuration.__detect_rimworld_steam() != "":
        if not os.path.isdir(steamworkshopdir):
            errormsg(wait_on_error,
                     "steam workshop directory '{}' could not be found. please check your installation and / or configuration file.".format(
                         steamworkshopdir))
            sys.exit(1)
        mod_data_workshop = load_mod_data(cat, database, steamworkshopdir, "W")

localmoddir = rimworld_configuration.get_mods_local_dir()
if not os.path.isdir(localmoddir):
    errormsg(wait_on_error,
             "local mod directory '{}' could not be found. please check your installation and / or configuration file.".format(
                 localmoddir))
    sys.exit(1)
mod_data_local = load_mod_data(cat, database, localmoddir, "L")

mod_data_full = {**mod_data_local, **mod_data_workshop}

mods_data_active = list()
for mods in mods_enabled_list:
    try:
        mods_data_active.append([mods, mod_data_full[mods][1]])

    except KeyError:
        pass
        # print("Unknown mod ID {}, deactivating it from mod list.".format(mods))

time.sleep(1)
print("")
print("sorting mods.")
newlist = sorted(mods_data_active, key=itemgetter(1))
print("")
print("{} subscribed mods, {} ({} known, {} unknown) enabled mods".format(len(mod_data_full), len(mods_enabled_list),
                                                                          len(mods_data_active) + 1, len(mod_unknown)))
# do backup
now_time = time.strftime('%Y%m%d-%H%M', time.localtime(time.time()))
shutil.copy(modsconfigfile, modsconfigfile + '.backup-{}'.format(now_time))

if not os.path.isfile(modsconfigfile):
    errormsg(wait_on_error, "error accessing " + modsconfigfile)
    sys.exit(1)
doc = ET.parse(modsconfigfile)
xml = doc.getroot()
xml = xml.find('activeMods')
for li in xml.findall('li'):
    xml.remove(li)

# ET.dump(doc)

xml_sorted = ET.SubElement(xml, 'li')
for mods in newlist:
    # print(mods)
    if mods[0] == "":
        print("skipping, empty?")
    else:
        xml_sorted = ET.SubElement(xml, 'li')
        xml_sorted.text = str(mods[0])
    # ET.dump(doc)

### finish
write_modsconfig = False
if mod_unknown:
    DB = dict()
    DB['time'] = str(time.ctime())
    print("")
    print("list of unknown mods:")
    for mods in mod_unknown:
        print("- {}".format(mods))
        DB[mods] = "not_categorized"
    print("")
    unknownfile = "rwms_unknown_mods_{}.json.txt".format(now_time)
    print("writing unknown mods to {}. Please submit this file to https://gitlab.com/rwms/rwmsdb/issues".format(
        unknownfile))
    with open(unknownfile, "w", encoding="UTF-8", newline="\n") as f:
        json.dump(DB, f, indent=True, sort_keys=True)
    f.close()

    while True:
        data = input("Do you REALLY want to write ModsConfig.xml (unknown mods are removed from loading) (y/n): ")
        if data.lower() in ('y', 'n'):
            break

    if data.lower() == 'y':
        write_modsconfig = True
else:
    print("lucky, no unknown mods detected!")
    write_modsconfig = True

if write_modsconfig:
    print("Writing new ModsConfig.xml.")
    doc.write(modsconfigfile, encoding='UTF-8', xml_declaration='False')
    print("Writing done.")
else:
    print("ModsConfig.xml was NOT modified.")

time.sleep(3)
if wait_on_exit:
    print("")
    input("Press ENTER to close the program.")
