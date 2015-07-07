PyPS3checker - Python checker script for PS3 flash memory dump files
Copyright (C) 2015 littlebalup@gmail.com
-------------------------------------------------------------------


Disclaimer:
----------
WARNING: Use this software at your own risk. The author accepts no
responsibility for the consequences of your use of it.


System requirements:
-------------------
 - Any system able to run Python 2.7.x (Windows, Linux, MAC... )
 - Python 2.7.2 or any upper Python 2 version : https://www.python.org 

 
Features:
--------
Compatible with any type of PS3 flash memory dump file: 
 - Regular NOR dump (teensy, progskeet, dumps from homebrew)
 - Reversed NOR dump (E3 flasher)
 - Interleaved NAND dump
 
Customization of checks and hashs can be done by editing the "checklist.xml" and "hashlist.xml" files.
All initial checks are those from PS3dumpchecker (many thanks at Swizzy), plus a "risklevel" parameter
that can be "WARNING" or "DANGER" like on the BwE validators.

Check log auto-generated as "[mydump].checklog.txt"


Usage:
-----
To display help/commands list, simply run the script without any argument.
 - from windows command prompt: 
        checker.py
 - from Linux/MAC console: 
        ./checker.py
   (under Unix systems, do not forget to set the script as executable using "chmod")

   
Command: 
	checker.py [input_file]

	 [input_file] : Dump filename to check."

	Examples :
	  (windows)
		checker.py mydump.bin  
		checker.py "D:\myfiles\mydump.bin"
	  (unix)
		./checker.py mydump.bin 
		./checker.py /home/username/myfiles/mydump.bin
		
   
Returned exit code:
    0 = checks competed with success. No "WARNING" or "DANGER" found.
    1 = one error occurred (script error, missing file...)
    2 = checks competed with at least a "WARNING" found. No "DANGER" found.
    3 = checks competed with at least a "DANGER" found.

   

   
   











