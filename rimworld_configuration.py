# RimWorld configuration file
#
# enter here your correct paths
import os
import sys

if sys.platform == "win32":
    import winreg


# "internal" detection routines, do not use outside of module
def __detect_rimworld_steam():
    steampath = ""
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
    # TODO: implement detect DRM free RimWorld.
    return ""


def __detect_rimworld():
    path = __detect_rimworld_steam()
    if path == "":
        path = __detect_rimworld_local()
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

    return rimworld_configdir


# directory detection routines
def get_mods_steamworkshop_dir():
    modsdir = __detect_rimworld_steam() + "/steamapps/workshop/content/294100"
    if not os.path.isdir(modsdir):
        return ""
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
        return ""
    else:
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
