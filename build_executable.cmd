@echo off
rem you need PyInstaller for generating the executable.

set version=
set /P version=<VERSION

set builddir=.builds\%version%
echo %builddir%

echo Building %version%.
if exist %builddir% rmdir /s /q %builddir%
mkdir %builddir%
cd %builddir%

where /q pyinstaller
if errorlevel 1 goto no_pyinstaller

where /q zip
if errorlevel 1 goto no_zip

goto start
:no_pyinstaller
echo PyInstaller not found.
echo.
echo You can obtain it at http://www.pyinstaller.org/downloads.html
echo Follow the instructions there.
echo.
goto byebye

:no_zip
echo zip utility not found.
echo.
echo You can obtain it the https://sourceforge.net/projects/infozip/files/
echo Download the Zip package, extract it somewhere in the PATH.
echo.
goto byebye

:start
pyinstaller --onefile ..\..\rwms_sort.py
copy ..\..\rwms_config.ini dist\
move dist\rwms_sort.exe dist\rwms_sort-%version%.exe

rem -- creating zip archives
rem Windows
zip -mj9 dist\rwms_sort-%version%-win.zip dist\rwms_sort-%version%.exe dist\rwms_config.ini
cd ..\..

rem build source archive
zip -j9 .builds\%version%\dist\rwms_sort-%version%-source.zip *.py *.cmd *.bat *.sh rwms_config.ini *.md LICENSE VERSION
goto byebye

:byebye
pause