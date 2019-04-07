# RimWorld configuration file
#
# enter here your correct paths
import configparser
import os
import sys

if sys.platform == "win32":
    import winreg


## do not use directly
def __load_value_from_config(entry):
    configfile = os.path.dirname(__file__) + "/rwms_config.ini"
    if not os.path.isfile(configfile):
        return ""

    cfg = configparser.ConfigParser()
    try:
        cfg.read(configfile)
    except:
        print("Error reading configuration file {}.".format(configfile))
        sys.exit(1)

    try:
        value = cfg.get("rwms", entry, raw=True)
    except:
        print("Error reading entry {} from configuration file {}".format(entry, configfile))
        sys.exit(1)

    return value


# "internal" detection routines, do not use outside of module
def __detect_rimworld_steam():
    steampath = __load_value_from_config("steamdir")
    key = None

    # TODO: implement Steam detection on other platforms than Windows.
    if sys.platform == "win32":
        registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        if registry:
            try:
                key = winreg.OpenKey(registry, "SOFTWARE\WoW6432Node\Valve\Steam")
            except:
                steampath = ""
            if key:
                steampath, regtype = winreg.QueryValueEx(key, "InstallPath")
        winreg.CloseKey(registry)

    return steampath


def __detect_rimworld_local():
    # TODO: implement automatic detection of DRM free RimWorld.
    drmfreepath = __load_value_from_config("drmfreedir")
    return drmfreepath


def __detect_rimworld():
    path = __detect_rimworld_steam()
    if path == "":
        path = __detect_rimworld_local()

    # sanity check
    if not os.path.isdir(path):
        return ""
    else:
        return path


def __detect_rimworld_configdir():
    # autodetect configuration directory (for ModsConfig.xml)
    rimworld_configdir = ""
    if sys.platform == "win32":
        rimworld_configdir = os.environ[
                                 "USERPROFILE"] + "/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config"
    elif sys.platform == "linux":
        rimworld_configdir = os.environ["HOME"] + "/.config/unity3d/Ludeon Studios/RimWorld"
    elif sys.platform == "darwin":
        rimworld_configdir = os.environ["HOME"] + "Library/Application Support/RimWorld/Config"

    # fallback to configuration file
    if not os.path.isdir(rimworld_configdir):
        rimworld_configdir = __load_value_from_config("configdir")

    return rimworld_configdir


# directory detection routines
def get_mods_steamworkshop_dir():
    modsdir = __detect_rimworld_steam() + "/steamapps/workshop/content/294100"
    if not os.path.isdir(modsdir):
        modsdir = __load_value_from_config("workshopdir")
        if not os.path.isdir(modsdir):
            modsdir = ""

    return modsdir


def get_mods_local_dir():
    modsdir = ""
    steampath = __detect_rimworld_steam()

    if steampath != "":
        modsdir = steampath + "/steamapps/common/RimWorld/Mods"
    else:
        drmfreepath = __detect_rimworld_local()
        # TODO: implement correct DRM free detection, need DRM free build
        if drmfreepath != "":
            modsdir = drmfreepath + "/Mods"

    if not os.path.isdir(modsdir):
        # fallback to configuration file
        modsdir = __load_value_from_config("modslocaldir")
        if not os.path.isdir(modsdir):
            modsdir = ""

    return modsdir


def get_modsconfigfile():
    configdir = __detect_rimworld_configdir() + "/ModsConfig.xml"
    if os.path.isfile(configdir):
        return configdir
    else:
        return ""


# debug
if __name__ == '__main__':
    print("Current OS agnostic configuration")
    print("RimWorld folder .................: " + __detect_rimworld())
    print("RimWorld configuration folder ...: " + __detect_rimworld_configdir())
    print("RimWorld local mods folder ......: " + get_mods_local_dir())
    print("RimWorld steam workshop folder ..: " + get_mods_steamworkshop_dir())

    pass
