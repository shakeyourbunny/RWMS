#!/usr/bin/python3
# RimWorld Module Sorter

import json
import os
import shutil
import sys
import time
import xml.etree.ElementTree as ET
from operator import itemgetter

import rimworld_configuration
import rwms_database

######################################################################################################################
# some basic initialization

if rimworld_configuration.__detect_rimworld() == "":
    print("no valid RimWorld installation detected!")
    sys.exit(1)

categories_url = 'https://gitlab.com/rwms/rwmsdb/raw/master/rwms_db_categories.json'
database_url = "https://gitlab.com/rwms/rwmsdb/raw/master/rwmsdb.json"
database_file = "rwms_database.json"

mod_unknown = list()


######################################################################################################################
# functions - read in mod data
def load_mod_data(cats, db, basedir, modsource):
    mod_details = dict()
    folderlist = os.listdir(basedir)
    for moddirs in folderlist:
        aboutxml = basedir + '/' + moddirs + "/About/About.xml"
        if os.path.isfile(aboutxml):
            xml = ET.parse(aboutxml)
            name = xml.find('name').text

            if name in db:
                try:
                    score = cats[db[name]][0]
                except:
                    print("FIXME: mod '{}' has an unknown category '{}'. stop.".format(name, db[name]))
                    print("please report this error to the database maintainer.")
                    sys.exit(1)

                # print("mod {} has a score of {}".format(name, score))
                try:
                    mod_entry = [moddirs, float(score), name, modsource]

                except KeyError:
                    print("could not construct dictionary entry for mod {}, score {}".format(name, score))
                    sys.exit(1)
            else:
                # print("mod {} is not in database, adding to unknown list.".format(name))
                mod_unknown.append(name)
                mod_entry = list()

            if mod_entry:
                mod_details[moddirs] = mod_entry
        else:
            print("could not find metadata for item " + moddirs + " (skipping)!")
            name = ""
    return mod_details


######################################################################################################################
# real start of the script

# load scoring mapping dict
cat = rwms_database.load_categories_mapping(categories_url)
if not cat:
    print("Could not load properly categories.")
    sys.exit(1)

# preload all needed data
# categories
score_db = "testdata/db_modscoring.json"
if not os.path.isfile(score_db):
    print("could not load db scoring table.")
    sys.exit(1)

# load the mod database
rwms_database.download_database(database_url, database_file)
database = rwms_database.load_database(database_file)
if not database:
    print("Error loading scoring database {}.".format(score_db))
    sys.exit(1)

print('Number of Mods registered in DB : {}'.format(len(database) - 2))
print('Last DB updated date : {}'.format(database['_db_time']))
print("")

modsconfigfile = rimworld_configuration.get_modsconfigfile()
print("Loading and parsing ModsConfig.xml")
if not os.path.isfile(modsconfigfile):
    print("could not find " + modsconfigfile)
    sys.exit(1)
xml = ET.parse(modsconfigfile)
xml = xml.find('activeMods')
mods_enabled_list = [t.text for t in xml.findall('li')]
if not "Core" in mods_enabled_list:
    mods_enabled_list.append("Core")

# check auf unknown mods
print("loading mod data.")
mod_data_workshop = dict()
mod_data_local = dict()

steamworkshopdir = rimworld_configuration.get_mods_steamworkshop_dir()
localmoddir = rimworld_configuration.get_mods_local_dir()

if steamworkshopdir != "":
    mod_data_workshop = load_mod_data(cat, database, steamworkshopdir, "W")
mod_data_local = load_mod_data(cat, database, localmoddir, "L")

mod_data_full = {**mod_data_local, **mod_data_workshop}

mods_data_active = list()
for mods in mods_enabled_list:
    try:
        mods_data_active.append([mods, mod_data_full[mods][1]])

    except KeyError:
        pass
        # print("Unknown mod ID {}, deactivating it from mod list.".format(mods))

print("sorting mods.")
newlist = sorted(mods_data_active, key=itemgetter(1))
print("")
print("{} subscribed mods, {} ({} known, {} unknown) enabled mods".format(len(mod_data_full), len(mods_enabled_list),
                                                                          len(mods_data_active), len(mod_unknown)))
# do backup
now_time = time.strftime('%Y%m%d-%H%M', time.localtime(time.time()))
shutil.copy(modsconfigfile, modsconfigfile + '.backup-{}'.format(now_time))

if not os.path.isfile(modsconfigfile):
    print("error accessing " + modsconfigfile)
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
    unknownfile = "rwms_unknown_mods_{}.json".format(now_time)
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
