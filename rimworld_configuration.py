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

    if steampath == "":
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

    return path


def __detect_rimworld_configdir():
    rimworld_configdir = __load_value_from_config("configdir")

    if rimworld_configdir == "":
        if sys.platform == "win32":
            rimworld_configdir = os.environ[
                                     "USERPROFILE"] + "/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config"
        elif sys.platform == "linux":
            rimworld_configdir = os.environ["HOME"] + "/.config/unity3d/Ludeon Studios/RimWorld"
        elif sys.platform == "darwin":
            rimworld_configdir = os.environ["HOME"] + "Library/Application Support/RimWorld/Config"

    return rimworld_configdir


# directory detection routines
def get_mods_steamworkshop_dir():
    modsdir = __load_value_from_config("workshopdir")

    if modsdir == "":
        modsdir = __detect_rimworld_steam() + "/steamapps/workshop/content/294100"

    return modsdir


def get_mods_local_dir():
    modsdir = __load_value_from_config("localmodsdir")
    if modsdir == "":
        steampath = __detect_rimworld_steam()

        if steampath != "":
            modsdir = steampath + "/steamapps/common/RimWorld/Mods"
        else:
            drmfreepath = __detect_rimworld_local()
            # TODO: implement correct DRM free detection, need DRM free build
            if drmfreepath != "":
                modsdir = drmfreepath + "/Mods"

    return modsdir


def get_modsconfigfile():
    return __detect_rimworld_configdir() + "/ModsConfig.xml"


# debug
if __name__ == '__main__':
    print("Current OS agnostic configuration")
    if __detect_rimworld_steam() != "":
        print("")
        print("Steam is on .....................: " + __detect_rimworld_steam())
        print("")
    print("RimWorld folder .................: " + __detect_rimworld())
    print("RimWorld configuration folder ...: " + __detect_rimworld_configdir())
    print("RimWorld local mods folder ......: " + get_mods_local_dir())
    print("RimWorld steam workshop folder ..: " + get_mods_steamworkshop_dir())

    print("RimWorld ModsConfig.xml .........: " + get_modsconfigfile())

    pass
