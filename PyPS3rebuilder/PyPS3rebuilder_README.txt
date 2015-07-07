PyPS3rebuilder - Python script to rebuild PS3 flash memory dump files
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
 
Other requirements:
-------------------
 - A valid "donor" ps3 flash memory dump file matching your PS3 model.
   No matter if is byte reversed or not, the script will take care of that.

 
Features:
--------
This script copy part or totality of non-PerConsole datas from a donor dump
file to a corrupted dump file in order to rebuild it.

Compatible with any type of PS3 flash memory dump file: 
 - Regular NOR dump (teensy, progskeet, dumps from homebrew)
 - Reversed NOR dump (E3 flasher)
 - Interleaved NAND dump
 
 
Usage:
-----
To display help/commands list, simply run the script without any argument.
 - from windows command prompt: 
        rebuilder.py
 - from Linux/MAC console: 
        ./rebuilder.py
   (under Unix systems, do not forget to set the script as executable using "chmod")

   
Command: 

	rebuilder.py [command] [input_file] [donor_file] [output_file]

	  [command]   Command from the list:
					  all    : copy all non-PerConsole datas
					  all-   : copy all non-PerConsole less PerFirmware datas
					  fstgen : copy First region generics only
					  frtbl  : copy Flash Region Table only
					  ccsd   : copy cCSD datas only
					  perfw  : copy PerFirmware datas only
					  cvtrm  : copy cVTRM datas only
					  secgen : copy Second region generics only
	 [input_file]  Original (corrupted) dump filename.
	 [donnor_file] Donor (healthy) dump filename.
	 [output_file] Saved generated filename (optional). If not defined, will be
				   saved as "[input_file].rebuilt.bin" .

	 Examples:
	  rebuilder.py all myCorruptedDump.bin healtyDonorDump.bin
	  rebuilder.py cvtrm myCorruptedDump.bin healtyDonorDump.bin myRebuiltDump.bin

  
Returned exit code:
    0 = command done with success.
    1 = one error occurred (script error, verification error, missing file...)

   

   
   











