rem @echo off
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

set use_7zip=no

if exist "%PROGRAMFILES%\7-zip\7z.exe" set use_7zip=yes
if "%use_7zip%" == "yes" set zipexec="%PROGRAMFILES%\7z.exe a -tzip -mx9 -r "
if "%use_7zip%" == "yes" set zipexec_move="%PROGRAMFILES%\7z.exe a -tzip -mx9 -sdel "
if "%use_7zip%" == "yes" goto start

where /q zip
if errorlevel 1 goto no_zip
set zipexec=zip -j9
set zipexec_move=zip -mj9

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
%zipexec_move% rwms_sort-%version%-win.zip rwms_sort-%version%.exe rwms_config.ini
goto byebye

:byebye
pause
