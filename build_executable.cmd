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

if exist "C:\Program Files\7-Zip\7z.exe" goto start
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
cd dist
if exist rwms_sort-%version%-win.zip del rwms_sort-%version%-win.zip
if exist "C:\Program Files\7-Zip\7z.exe" (
  "C:\Program Files\7-Zip\7z.exe" a -tzip -mx9 -sdel rwms_sort-%version%-win.zip rwms_sort-%version%.exe rwms_config.ini
) else (
  zip -mj9 rwms_sort-%version%-win.zip rwms_sort-%version%.exe rwms_config.ini
)
cd ..\..\..

rem build source archive
if exist .builds\%version%\dist\rwms_sort-%version%-source.zip del .builds\%version%\dist\rwms_sort-%version%-source.zip
if exist "C:\Program Files\7-Zip\7z.exe" (
  "C:\Program Files\7-Zip\7z.exe" a -tzip -mx9 -r .builds\%version%\dist\rwms_sort-%version%-source.zip *.py *.cmd *.bat *.sh rwms_config.ini *.md LICENSE VERSION
) else (
  zip -j9 .builds\%version%\dist\rwms_sort-%version%-source.zip *.py *.cmd *.bat *.sh rwms_config.ini *.md LICENSE VERSION
)
goto byebye

:byebye
pause