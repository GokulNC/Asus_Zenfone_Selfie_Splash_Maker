:: Created By Gokul NC

@echo off
echo.--------------------------------------
echo.Asus Zenfone Splash (HD/FHD) Image Maker

:: This is for Asus Zenfone devices only, please do not try on other devices..
:: For other devices: http://forum.xda-developers.com/android/software-hacking/guide-how-to-create-custom-boot-logo-t3470473

echo.
echo.	By **Gokul NC**
echo.--------------------------------------
echo.
echo.
echo.Creating splash.img ........
echo.
echo.
echo.

setlocal
if not exist "output\" mkdir "output\"
if not exist "temp\" ( mkdir "temp\"& attrib /S /D +h "temp" )
del /Q temp\* 2>NUL
del /Q "output\splash.img" 2>NUL

::Create splash.img
:: I have included a minimal copy of Python (Windows) with required libraries (instead of asking users to install them)
bin\Python2.7\python2.7.exe bin\Asus_Zenfone_Selfie_Splash_Maker_Utility.py "output\splash.img" || (echo."PROCESS FAILED. Try Again"&echo.Quitting&echo.&pause&exit)

:: 'splash' partition size of Zenfone Selfie is 5MB; so splash.img shouldn't be larger than that.. No idea about other devices.
set max_file_size=5368709120
call :set_file_size "output\splash.img"
if %file_size% gtr %max_file_size% ( echo."splash.img generated is larger than 5MB, which is not recommended"&echo."Reduce picture resolution and try again"&echo.&echo.&pause&exit )

if exist "output\splash.img" ( echo.SUCCESS!&echo. splash.img created in "output" folder
) else ( echo.PROCESS FAILED.. Try Again&echo.&echo.&pause&exit )

echo.&echo.&set /P INPUT=Do you want to create a flashable zip? [yes/no]
If /I "%INPUT%"=="y" goto :CREATE_ZIP
If /I "%INPUT%"=="yes" goto :CREATE_ZIP

echo.&echo.&echo Flashable ZIP not created..&echo.&echo.&pause&exit

:CREATE_ZIP
copy /Y bin\New_Splash.zip "output\flashable_splash.zip" >NUL
cd output
..\bin\7za a flashable_splash.zip splash.img >NUL
cd..

if exist "output\flashable_splash.zip" (
 echo.&echo.&echo.SUCCESS!
 echo.Flashable zip file created in "output" folder
 echo.You can flash the 'flashable_splash.zip' from any custom recovery like TWRP or CWM or Philz
) else ( echo.&echo.&echo Flashable ZIP not created.. )

echo.&echo.&pause&exit

:set_file_size
:: Reference: http://stackoverflow.com/a/29846647/5002496
set file_size=%~z1
goto :eof