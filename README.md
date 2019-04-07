# RWMS - RimWorld Mod Sorter
#### Links
Homepage: https://gitlab.com/rwms/rwms 

Issues: https://gitlab.com/rwms/rwms/issues (for database contribution: https://gitlab.com/rwms/rwmsdb/issues)

Discussion thread on Ludeon: tbd

## Description

This Python script sorts your ModConfigs.xml (RimWorld mod configuration) for better loading time 
putting the dependencies of your mod order in the right spot. This is also the only function of the 
script, it will do this one thing and nothing else. 

Managing mods ((un)subscribing, mod load lists etc) is beyond the scope of this script, there 
is a better ingame solution called "Mod Manager" by Fluffy. The only thing it does, is optimizing
the mod load order.

For using the script you need an active internet connection which will connect to Gitlab, where
the current sort order database resides.

Descripton of the database see https://gitlab.com/rwms/rwmsdb/blob/master/README.md

## Usage

Just run the script with 
> python rwms_sort.py
 
or

> python36 rwms_sort.py

or (Windows)

> rwms_sort.bat

or (Linux)

> rwms_sort.sh

There should be no interactions (except writing ModsConfig.xml if you have unknown mods).

If some mods are unknown, the script will generate a *rws_unknown_mods_YYYYmmdd-HHMM.json* file,
where all unknown mods are listed. Please submit this file in the forum thread or in the sister
project, RWMSDB on https://gitlab.com/rwms/rwmsdb/issues  

## Installation
### Python 3.6+

You need a Python 3.6+ installation on your computer. This script does not work with Python 2 or
Python 3 distributions less then 3.6. This script does not need extra Python modules.

#### Windows
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


### RWMS installation
Download https://gitlab.com/rwms/rwms/-/archive/master/rwms-master.zip and decompress it in a 
folder of your liking. 

## Configuration file
The configuration file *rwms_config.ini* is only needed if the autodetection fails (or on other 
platforms than Windows / Steam). Just open the configuration in your favorite text editor (NOT
Microsoft Word) and you can modify all paths there. 

There are no default values, you have to fill them in for yourself.

entry | description
--- | ---
steamdir | path to your steam installation (not the game itself).
drmfreedir | path to your DRM-free RimWorld game installation, not used for a steam installation (and vice versa).
configdir | path to the main RimWorld configuration directory in your user profile.
workshopdir | path to your RimWorld steam workshop directory (ends with the steam appid). 
localmodsdir | path to your locally installed RimWorld mods in the RimWorld game directory (ends with Mods).

You may have to use quotes, if the path has spaces in it and always provide the full path. 

NB: you always can check your (detected) configuration with
> python rwms_configuration.py

in your shell (Windows Command Line, Linux shell)
## History
See https://gitlab.com/rwms/rwms/commits/master

This script is written from scratch and shares no code with the "other" RimWorld mod 
sorter by zzz465. My script also has its own, incompatible scoring system.

## License
Script written by shakeyourbunny <shakeyourbunny@gmail.com> 

RWMS is licensed under the GNU GPL v2.

Note that you are not allowed to take parts of the scripts for using them in your own mod sorting or
mod manager scripts without written permission. 
