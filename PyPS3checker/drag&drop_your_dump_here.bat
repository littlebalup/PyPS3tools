@title PyPS3checker launcher
@echo off

if [%1]==[] goto usage

cd /D "%~dp0"

"python" checker.py %1
echo.
echo.
Choice /M "This window will be closed. Do you want to open log file?"
if %errorlevel%==1 goto openlog
if %errorlevel%==2 goto end

:openlog
%1.checklog.txt
goto end

:usage
echo.
echo Usage :
echo If not yet done, install Python 3.x and add installation path to PATH environment variable.
echo Then drag and drop your dump file to this Batch file.
echo.
pause

:end
exit