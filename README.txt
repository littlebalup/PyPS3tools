PyPS3checker - Python checker script for PS3 flash memory dump files
Copyright (C) 2015 littlebalup@gmail.com
-------------------------------------------------------------------

*** "Standalone package for Windows" edition ***


Disclaimer:
----------
WARNING: Use this software at your own risk. The author accepts no
responsibility for the consequences of your use of it.


System requirements:
-------------------
Windows x86 or x64 (tested on XP, 7, 10) 
Microsoft Visual C++ 2008 Redistributable Package (vcredist_x86.exe) if not yet installed :
   http://www.microsoft.com/downloads/details.aspx?FamilyID=9b2da534-3e03-4391-8a4d-074b9f2bc1bf&displaylang=en

 
Features:
--------
Compatible with any type of PS3 flash memory dump file: 
 - Regular NOR dump (teensy, progskeet, dumps from homebrew, from PS3Xploit)
 - Reversed NOR dump (E3 flasher)
 - Full interleaved NAND dump, PS3Xploit NAND dump
 - EMMC dump from PS3Xploit (still in WIP)
 
Customization of checks and hashs can be done by editing the ".\dist\checklist.xml" and ".\dist\hashlist.xml" files.
All initial checks are those from PS3dumpchecker (many thanks at Swizzy), plus a "risklevel" parameter
that can be "WARNING" or "DANGER" like on the BwE validators.

Check log auto-generated as "[mydump].checklog.txt"


Usage:
-----
Simply drag and drop your dump file to the "drag&drop_your_dump_here.bat" file.


Alternatively, you can run the .\dist\checker.exe executable from Windows command prompt: 

To display help/commands list, simply run the exe without any argument.
   
Command: 
	checker.exe [input_file]

	 [input_file] : Dump filename to check."

	Examples :
		checker.exe mydump.bin  
		checker.exe "D:\myfiles\mydump.bin"
   
Returned exit code:
    0 = checks competed with success. No "WARNING" or "DANGER" found.
    1 = one error occurred (script error, missing file...)
    2 = checks competed with at least a "WARNING" found. No "DANGER" found.
    3 = checks competed with at least a "DANGER" found.

   

   
   











