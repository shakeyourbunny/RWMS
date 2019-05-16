#!/usr/bin/env python3
"""
configuration module for RWMS
"""
import configparser
import os
import sys

if sys.platform == "win32":
    import winreg


def configuration_file():
    """
    returns the configuration file as a string, empty if not detected.
    :return: str
    """

    # check, if script is compiled with pyinstaller
    mypath = str()

    if getattr(sys, 'frozen', False):
        mypath = os.path.dirname(sys.executable)
    elif __file__:
        mypath = os.path.dirname(sys.argv[0])

    return os.path.join(mypath, "rwms_config.ini")


def load_value(section, entry, isBool=False):
    """
    loads a value from the configurato
    :param section: configuration file section
    :param entry: entry
    :param isBool: optional, if it is a boolean switch
    :return: value
    """
    configfile = configuration_file()

    if not os.path.isfile(configfile):
        return ""

    cfg = configparser.ConfigParser()
    try:
        cfg.read(configfile)
    except:
        print("Error parsing configuration file {}.".format(configfile))
        sys.exit(1)

    try:
        if isBool:
            value = cfg.getboolean(section, entry)
        else:
            value = cfg.get(section, entry, raw=True)
    except:
        print("Error parsing entry '{}', section '{}' from configuration file '{}'".format(entry, section, configfile))
        sys.exit(1)
    return value


def detect_steam():
    """
    automatic detection of steam
    :return: path to steam base directory
    """
    disablesteam = load_value("rwms", "disablesteam", True)
    if disablesteam:
        return ""
    steampath = load_value("paths", "steamdir")
    key = None
    if steampath == "":
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
        elif sys.platform == "darwin":
            steampath = os.environ["HOME"] + "/Library/Application Support/Steam"
        elif sys.platform == "linux":
            steampath = os.environ["HOME"] + "/.steam/steam"
    return steampath


def detect_rimworld_steam():
    rwsteampath = detect_steam()
    if rwsteampath != "":
        if sys.platform == "win32":
            rwsteampath = os.path.join(rwsteampath, "steam", "steamapps", "common", "RimWorld")
        elif sys.platform == "darwin":
            rwsteampath = os.path.join(rwsteampath, "steamapps", "common", "RimWorld", "RimWorldMac.app")
        elif sys.platform == "linux":
            rwsteampath = os.path.join(rwsteampath, "steamapps", "common", "RimWorld")
    return rwsteampath

def detect_rimworld_local():
    """
    detects local drmfree RimWorld installation (has to be configured via configuration file)
    :return: path to RimWorld installation
    """
    drmfreepath = load_value("paths", "drmfreedir")
    return drmfreepath


def detect_rimworld():
    """
    generic detection of RimWorld installation
    :return: path to RimWorld installation
    """
    path = detect_rimworld_steam()
    if path == "":
        path = detect_rimworld_local()
    return path


def detect_rimworld_configdir():
    """
    detects RimWorld configuration directory (savegames etc)
    :return: path to RimWorld configuration
    """
    rimworld_configdir = load_value("paths", "configdir")
    if rimworld_configdir == "":
        if sys.platform == "win32":
            rimworld_configdir = os.environ[
                                     "USERPROFILE"] + "/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config"
        elif sys.platform == "linux":
            rimworld_configdir = os.environ["HOME"] + "/.config/unity3d/Ludeon Studios/RimWorld by Ludeon Studios/Config"
        elif sys.platform == "darwin":
            rimworld_configdir = os.environ["HOME"] + "/Library/Application Support/RimWorld/Config"
    return rimworld_configdir


def detect_steamworkshop_dir():
    """
    detects steamworkshop directory if steam version
    :return: path to workshop directory
    """
    if load_value("rwms", "disablesteam", True):
        return ""
    modsdir = load_value("paths", "workshopdir")
    if modsdir == "":
        modsdir = os.path.join(detect_steam(), "steamapps", "workshop", "content", "294100")
    return modsdir


def detect_localmods_dir():
    """
    detects local mods directory for RimWorld
    :return: path to localmods directory
    """
    modsdir = load_value("paths", "localmodsdir")
    if modsdir == "":
        steampath = detect_rimworld_steam()
        if steampath != "":
            modsdir = os.path.join(steampath, "Mods")
        else:
            drmfreepath = detect_rimworld_local()
            if drmfreepath != "":
                os.path.join(drmfreepath, "Mods")
    return modsdir


def modsconfigfile():
    """
    ModsConfig.xml
    :return: returns full path of ModsConfig.xml
    """
    return detect_rimworld_configdir() + "/ModsConfig.xml"


def __dump_configuration():
    """
    dumps complete configuration of RMWS to stdout
    """
    print("pyinstaller configuration")
    frozen = 'not'
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        frozen = 'ever so'
        bundle_dir = sys._MEIPASS
    else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    print('we are', frozen, 'frozen')
    print('bundle dir is', bundle_dir)
    print('sys.argv[0] is', sys.argv[0])
    print('sys.executable is', sys.executable)
    print('os.getcwd is', os.getcwd())
    print("")
    print("configuration file is {}\n".format(configuration_file()))
    print("Current OS agnostic configuration")
    if detect_rimworld_steam() != "":
        print("")
        print("Steam is on .....................: " + detect_steam())
        print("")
    print("RimWorld folder .................: " + detect_rimworld())
    print("RimWorld configuration folder ...: " + detect_rimworld_configdir())
    print("RimWorld local mods folder ......: " + detect_localmods_dir())
    print("RimWorld steam workshop folder ..: " + detect_steamworkshop_dir())

    print("RimWorld ModsConfig.xml .........: " + modsconfigfile())
    print("")
    print("Updatecheck .....................: {}".format(load_value("rwms", "updatecheck")))
    print("Open Browser ....................: {}".format(load_value("rwms", "openbrowser")))
    print("Wait on Error ...................: {}".format(load_value("rwms", "waitforkeypress_on_error")))
    print("Wait on Exit ....................: {}".format(load_value("rwms", "waitforkeypress_on_exit")))
    print("Disable Steam Checks ............: {}".format(load_value("rwms", "disablesteam")))
    print("Do not remove unknown mods ......: {}".format(load_value("rwms", "dontremoveunknown")))
    print("Tweaks are disabled .............: {}".format(load_value("rwms", "disabletweaks")))
    print("")
    if load_value("github", "github_username"):
        print("GitHub username .................: is set, not displaying it.")
    if load_value("github", "github_password"):
        print("GitHub password  ................: is set, not displaying it.")


# debug
if __name__ == '__main__':
    __dump_configuration()

    print("")
    input("Press ENTER to end program.")
    pass
