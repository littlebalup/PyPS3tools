@title PyPS3checker launcher
@echo off

if [%1]==[] goto usage

cd /D "%~dp0"
cd dist

checker %1
echo.
echo.
Choice /M "This window will be closed. Do you want to open the log file?"
if %errorlevel%==1 goto openlog
if %errorlevel%==2 goto end

:openlog
%1.checklog.txt
goto end

:usage
echo PyPS3checker standalone
echo.
echo Usage :
echo Drag and drop your dump file to this Batch file.
echo.
pause

:end
exit