PyPS3patcher - Python patcher script for PS3 flash memory dump files
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
 
Patch FSM, noFSM, RVK (see detailed commands).
Byte reverse NOR dump (see "swap" command)
 
 
Usage:
-----
To display help/commands list and patch version, simply run the script without any argument.
 - from windows command prompt: 
        patcher.py
 - from Linux/MAC console: 
        ./patcher.py
   (under Unix systems, do not forget to set the script as executable using "chmod")

   
Command: 

	patcher.py [command] [input_file] [output_file]

	  [command]      Command from list:
						nofsm     : apply 4.XX noFSM ROS patches.
						nofsm_rvk : apply 4.XX noFSM ROS patches + RVK patches.
						fsm       : apply 3.55 FSM patches (ROS + RVK patches).
						cust      : apply a custom ROS patches.
						cust_rvk  : apply a custom ROS patches + RVK patches.
						swap      : byte reverse.
	  [input_file]   Original dump filename.
	  [output_file]  Saved generated filename (optional). If not defined, will be
					 saved as "[input_file].patched.bin" for patch commands or as
					 "[input_file].swaped.bin" for swap command.
	 NOTES :
	 - Custom ROS patch file must be nammed "patch.bin" and located to the script
	   folder.

	 Examples:
	  (windows)
		  patcher.py nofsm mydump.bin
		  patcher.py fsm mydump.bin mydump_patched.bin
		  patcher.py cust_rvk D:\myfolder\mydump.bin
	  (unix)
	      ./patcher.py nofsm mydump.bin
		  ./patcher.py fsm mydump.bin mydump_patched.bin
		  ./patcher.py cust_rvk /home/username/myfolder/mydump.bin

   
Returned exit code:
    0 = patches applied with success.
    1 = one error occurred (script error, verification error, missing file...)

   

   
   











