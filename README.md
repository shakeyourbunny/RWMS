# RWMS - RimWorld Mod Sorter

[Download](https://www.github.com/releases) (includes Windows executable)

![version](https://img.shields.io/github/release/shakeyourbunny/RWMS.svg?style=plastic "version")
[![Date Latest](https://img.shields.io/github/release-date/shakeyourbunny/RWMS.svg?style=plastic)](https://github.com/shakeyourbunny/RWMS/releases/latest)
[![Commits Since Latest](https://img.shields.io/github/commits-since/shakeyourbunny/RWMS/latest.svg?style=plastic)](https://github.com/shakeyourbunny/RWMS/commits/master)
![version](https://img.shields.io/github/downloads/shakeyourbunny/RWMS/total.svg?style=plastic "version")

#### Links
Homepage: https://github.com/shakeyourbunny/RWMS 

Discussion thread on Ludeon: https://ludeon.com/forums/index.php?topic=48518.0

## Description

This Python script sorts your ModConfigs.xml (RimWorld mod configuration) for better loading time 
putting the dependencies of your mod order in the right spot. This is also the only function of the 
script, it will do this one thing and nothing else. 

Managing mods ((un)subscribing, mod load lists etc) is beyond the scope of this script, there 
is a better ingame solution called "Mod Manager" by Fluffy. The only thing it does, is optimizing
the mod load order.

For using the script you need an active internet connection which will connect to Github, where
the current sort order database resides.

## Usage

Just run the script with 
> python rwms_sort.py
 
or

> python36 rwms_sort.py

or (Windows)

> rwms_sort.bat

or (Linux)

> rwms_sort.sh

There should be no interactions if not desired (except writing ModsConfig.xml if 
you have unknown mods).

If some mods are unknown, the script will generate a *rws_unknown_mods_YYYYmmdd-HHMM.json.txt* file,
where all unknown mods are listed. Please submit this file in the forum thread or in the sister
project, RWMSDB on https://github.com/shakeyourbunny/RWMSDB/issues  

## Upgrading
It is recommended that you do a clean installation, but you can copy over your 
rwms_config.ini in the new directory, but do not forget to check this documentation for
new (or changed) settings.

## Installation
### Python 3.6+

You need a Python 3.6+ installation on your computer. This script does not work with Python 2 or
Python 3 distributions less then 3.6. This script does not need extra Python modules.

#### Windows
Windows binary downloads are available on the release page. 

If you wish to use the source directly, see below.

Go to https://www.python.org/downloads/ and click on the big yellow "Download Python 3.7.x"
button, let the installer run and let Python be added to the search path.

After that you can start directly python (.py) files from the explorer, but I recommend using the 
batch file rwms_sort.bat, because the python script does not wait after execution and there will
just be some window flashing up due its nature of being a command-line program.

#### Linux distributions
Many distributions still have Python 2 as system default and RWMS is a pure Python 3 script; I did
not test it with Python 2 and it uses some more recent features of 3, so you have to check, if 
your default python version with
> python --version

Mostly, this will be 2.7, so you have to install Python 3 too. 

Linux Distribution     | Source | How to install
--- | --- | ---
Debian / Ubuntu / Mint | PPA            | https://askubuntu.com/questions/865554/how-do-i-install-python-3-6-using-apt-get#865569
Fedora (recent) | repo | sudo dnf install python37
CentOS 7 | repo | sudo yum install centos-release-scl && sudo yum install rh-python36
Arch Linux / Manjaro | repo | pacman -S python (should already be installed)

After this, please install the BeautifulSoup python module (Windows and Linux)

>pip install bs4

### RWMS installation
Download the source distribution from the releases page and unzip it in a 
folder of your liking. Alternatively, you can also clone the repository.

## Configuration file
The configuration file *rwms_config.ini* is only needed if the autodetection fails (or on other 
platforms than Windows / Steam). Just open the configuration in your favorite text editor (NOT
Microsoft Word) and you can modify all paths there. 

### General options
There are no default values, you have to fill them in for yourself.

entry | description
--- | ---
steamdir | path to your steam installation (not the game itself).
drmfreedir | path to your DRM-free RimWorld game installation, not used for a steam installation (and vice versa).
configdir | path to the main RimWorld configuration directory in your user profile.
workshopdir | path to your RimWorld steam workshop directory (ends with the steam appid). 
localmodsdir | path to your locally installed RimWorld mods in the RimWorld game directory (ends with Mods).

You may have to use quotes, if the path has spaces in it and always provide the full path. 

Additional parameters control if you want to enable the update check, waiting for keypresses and
optional automatic submitting unknown mods to the database issue tracker.

NB: you always can check your (detected) folder configuration with
> python rwms_configuration.py

in your shell (Windows Command Line, Linux shell)

### Update Check
entry | default value | description
--- | --- | ---
updatecheck | True | tells RWMS either to check for new updates or not. This is just a version check, no autoupdate.
openbrowser_on_update | False | opens a new (default) web browser window with the RWMS page, if a newer version is available.

### Interactive and misc options
These are the default options on waiting for keypresses etc.

entry | default value | description
--- | --- | ---
waitforkeypress_on_error | True | wait for a keypress / Enter after an error occurs.
waitforkeypress_on_exit | True | wait for a keypress / Enter to exit the program.

entry | default value | description
--- | --- | ---
disablesteam | False | ignore any steam installations or related stuff

### GitHub submission options
If you want your unknown mods automatically submitted as an issue, please configure these 
settings. They are fully optional.

entry | default value | description
--- | --- | ---
github_username | - | user name on GitHub
github_password | - | your GitHub password

## History
See https://github.com/shakeyourbunny/RWMS/blob/master/CHANGELOG

## Contributors
see https://github.com/shakeyourbunny/RWMS/blob/master/CONTRIBUTORS.md

## License
Script written by shakeyourbunny <shakeyourbunny@gmail.com> 

RWMS is licensed under the GNU GPL v2.

Note that you are not allowed to take parts of the scripts for using them in your own mod sorting or
mod manager scripts without written permission. 
