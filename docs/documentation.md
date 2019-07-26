# RWMS - RimWorld Mod Sorter

[Download](https://www.github.com/shakeyourbunny/RWMS/releases) (includes Windows executable)

![version](https://img.shields.io/github/release/shakeyourbunny/RWMS.svg?style=plastic "version")
[![Date Latest](https://img.shields.io/github/release-date/shakeyourbunny/RWMS.svg?style=plastic)](https://github.com/shakeyourbunny/RWMS/releases/latest)
[![Commits Since Latest](https://img.shields.io/github/commits-since/shakeyourbunny/RWMS/latest.svg?style=plastic)](https://github.com/shakeyourbunny/RWMS/commits/master)
![version](https://img.shields.io/github/downloads/shakeyourbunny/RWMS/total.svg?style=plastic "version")

#### Links
Homepage: https://github.com/shakeyourbunny/RWMS 

Discussion thread on Ludeon: https://ludeon.com/forums/index.php?topic=48518.0

## Table of contents
   * [Description](#description)
   * [Usage](#usage)
      * [Command Line Options](#command-line-options)
      * [Upgrading](#upgrading)
     * [Installation](#installation)
      * [Python 3.6 ](#python-36)
         * [Windows](#windows)
         * [Linux distributions](#linux-distributions)
         * [Mac OSX](#osx)
         * [Missing modules](#missing-modules)
      * [RWMS installation](#rwms-installation)
   * [Configuration file](#configuration-file)
      * [General options](#general-options)
      * [Update Check](#update-check)
      * [Interactive and misc options](#interactive-and-misc-options)
      * [GitHub submission options](#github-submission-options)
   * [Notes on the unknown mods file](#notes-on-the-unknown-mods-file)
   * [History](#history)
   * [Contributors](#contributors)
   * [License](#license)

## Description

This Python script sorts your ModConfigs.xml (RimWorld mod configuration) for better loading time 
putting the dependencies of your mod order in the right spot. This is also the only function of the 
script, it will do this one thing and nothing else. 

Managing mods ((un)subscribing, mod load lists etc) is beyond the scope of this script, there 
is a better ingame solution called "Mod Manager" by Fluffy. The only thing it does, is optimizing
the mod load order.

For using the script you need an active internet connection which will connect to Github, where
the current sort order database resides.

## Command Line Options
Option | Description
--- | ---
--help | displays helps and valid command line arguments
--disable-steam | force disable Steam checks
--dont-remove-unknown-mods | do not remove unknown mods
--dump-configuration | dumps the current configuration and exits
--contributors | list all contributors to the script and the database who have contributed more than 10 mods
--reset-to-core | reset ModsConfig.xml to just Core

Note that the switches which are named identical to the configuration options override these, so the
priority order of options is: **default settings - configuration file - command line arguments.**

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

If some mods are unknown, the script will generate a *rwms_unknown_mods_YYYYmmdd-HHMM.json.txt* file,
where all unknown mods are listed. Please submit this file in the forum thread or in the sister
project, RWMSDB on https://github.com/shakeyourbunny/RWMSDB/issues  

## Upgrading
It is recommended that you do a clean installation, but you can copy over your 
rwms_config.ini in the new directory, but do not forget to check this documentation for
new (or changed) settings.

## Installation
### Python 3.6+

You need a Python 3.6+ installation on your computer. This script does not work with Python 2 or
Python 3 distributions less then 3.6.

#### Windows
Windows binary downloads are no longer available for download after 0.94.7. Instead, 
if you wish to have a binary executable, use the included build_executable.cmd which
was used for generating these executables. You will need PyInstaller and zip for 
generating the executable.  

If you wish to use the source directly, see below.

Go to https://www.python.org/downloads/ and click on the big yellow "Download Python 3.7.x"
button, let the installer run and let Python be added to the search path.

After that you can start directly python (.py) files from the explorer, but I recommend using the 
batch file rwms_sort.bat. Default behaviour of RWMS is now that it will wait after a fatal error
and after it is finished. This may be changed through the configuration file, though.

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

#### OSX
Download and install Python via https://www.python.org/downloads/mac-osx/ (latest release).

#### Missing modules
After this, run install_requirements.sh (Linux / OSX) or install_requirements.cmd
to install missing Python modules.

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
dontremoveunknown | False | do not remove unknown mods from the ModsConfig.xml (and stick them at the bottom)

### GitHub submission options
If you want your unknown mods automatically submitted as an issue, please configure these 
settings. They are fully optional.

entry | default value | description
--- | --- | ---
github_username | - | user name on GitHub
github_password | - | your GitHub password

## Notes on the unknown mods file
If RWMS finds any unknown mods, they will be recorded on a rwms_unknown_mods_YYYYMMDD-HHMM.json.txt
file in the current working directory. This file may be submitted to the RWMSDB Github tracker or
will be automatically, if GitHub user credentials (see above) are provided. 

This data file includes the names of all unknown mods, timestamp of generation of the file and
(beginning with 0.94.1) some meta information about the installation: operating system, RimWorld
build number, type of operating system environment (Windows/Linux/OSX) and a version number. The 
latter describes the version of the data structure format and is used for merge tool for  the 
database in order to parse the file correctly.

#### datafile format history
##### original datafile version
included:
- timestamp
- list of unknown mods

##### original datafile version, revision 1
added:
- contributor name

##### original datafile version, revision 2 (0.94.0)
modified:
- contributor name: is autofilled with github user name

##### original datafile version,  revision 3 (0.94.1 pre-release)
added:
- number of unknown mods

##### datafile version v2/3 (0.94.1) 
added:
- datafile version number
- number of known mods
- operating system platform (win32, darwin, linux
- RimWorld build number
- RWMS version

modified:
- unknown mod entries now include steam workshop url, if steam detection is not disabled 
(disablesteam = False in configuration file)
- meta information has now its own category section in the datafile

##### datafile version v4 (0.94.7)
modified:
- cleaned up mod names (RimWorld version, mod versions)
- may lead to unknown mods in older revisions of the script

## History
See https://github.com/shakeyourbunny/RWMS/blob/master/CHANGELOG

## Contributors
see https://github.com/shakeyourbunny/RWMS/blob/master/CONTRIBUTORS.md

## License
Script written by shakeyourbunny <shakeyourbunny@gmail.com> 

RWMS is licensed under the GNU GPL v2.

Note that you are not allowed to take parts of the scripts for using them in your own mod sorting or
mod manager scripts without written permission. 
