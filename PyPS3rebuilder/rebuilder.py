#!/usr/bin/python
# -*- coding: utf-8 -*-

# *************************************************************************
# PyPS3rebuilder - Python scipt to rebuild PS3 flash memory dump files
#
# Copyright (C) 2015 littlebalup@gmail.com
#
# This code is licensed to you under the terms of the GNU GPL, version 2;
# see http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# *************************************************************************


import os
import sys
import time
import hashlib
import shutil


def getMD5(file):
    h = hashlib.md5()
    f = open(file, "rb")
    h.update(f.read())
    f.close()
    return h.hexdigest()    

def checkReversed(file):
    f = open(file,"rb")
    f.seek(0x14)
    bytes = f.read(0x4)  # FACEOFF
    if bytes == '\x0F\xAC\xE0\xFF':
        f.close()
        return False
    elif bytes == '\xAC\x0F\xFF\xE0':
        f.close()
        return True
    f.seek(0x1C)
    bytes = f.read(0x4)  # DEADBEEF
    if bytes == '\xDE\xAD\xBE\xEF':
        f.close()
        return False
    elif bytes == '\xAD\xDE\xEF\xBE':
        f.close()
        return True
    f.seek(0x200)
    bytes = f.read(0x4)  # IFI
    if bytes == '\x49\x46\x49\x00':
        f.close()
        return False
    elif bytes == '\x46\x49\x00\x49':
        f.close()
        return True
    f.seek(0x3F060)
    bytes = f.read(0x4)  # I.DL
    if bytes == '\x7F\x49\x44\x4C':
        f.close()
        return False
    elif bytes == '\x49\x7F\x4C\x44':
        f.close()
        return True
    f.seek(0xF00014)
    bytes = f.read(0x4)  # FACEOFF
    if bytes == '\x0F\xAC\xE0\xFF':
        f.close()
        return False
    elif bytes == '\xAC\x0F\xFF\xE0':
        f.close()
        return True
    f.seek(0xF0001C)
    bytes = f.read(0x4)  # DEADFACE
    if bytes == '\xDE\xAD\xFA\xCE':
        f.close()
        return False
    elif bytes == '\xAD\xDE\xCE\xFA':
        f.close()
        return True
    f.close()
    sys.exit("ERROR: unable to determine if file %s is byte reversed! Too much curruptions."%file)

def reverse(data):
    rev = ''.join([c for t in zip(data[1::2], data[::2]) for c in t])
    return rev

def writeBytesToFile(data, file):
    f = open(file,"wb")
    f.write(data)
    f.close

def copyDatas(donor, receiver, offset, length, swap):
    f = open(donor,"rb")
    f.seek(offset)
    if swap:
        datas = reverse(f.read(length))
    else:
        datas = f.read(length)
    f.close()
    f = open(receiver,"r+b")
    f.seek(offset)
    f.write(datas)
    f.close()
    print "done"
    print "  Verifying copied datas...",
    f = open(receiver,"rb")
    f.seek(offset)
    if datas != f.read(length):
        f.close()
        print
        sys.exit("ERROR: verification failed!")
    else:
        f.close()
        print "done"


if __name__ == "__main__":

    release = "v0.3"

    print
    print "  ____        ____  ____ _____          _           _ _     _           "
    print " |  _ \ _   _|  _ \/ ___|___ / _ __ ___| |__  _   _(_) | __| | ___ _ __ "
    print " | |_) | | | | |_) \___ \ |_ \| '__/ _ \ '_ \| | | | | |/ _` |/ _ \ '__|"
    print " |  __/| |_| |  __/ ___) |__) | | |  __/ |_) | |_| | | | (_| |  __/ |   "
    print " |_|    \__, |_|   |____/____/|_|  \___|_.__/ \__,_|_|_|\__,_|\___|_|   "
    print "        |___/                                                     %s "%release
    print
    print "Python script to rebuild PS3 flash memory dump files"
    print "Copyright (C) 2015 littlebalup@gmail.com"
    print
    if len(sys.argv) == 1:
        print "This script copy part or totality of non-PerConsole datas from a donor dump"
        print "file to a corrupted dump file in order to rebuild it."
        print
        print "Usage:"
        print "%s [command] [input_file] [donor_file] [output_file]"%(os.path.basename(__file__))
        print
        print "  [command]   Command from the list:"
        print "                  all    : copy all non-PerConsole datas"
        print "                  all-   : copy all non-PerConsole less PerFirmware datas"
        print "                  fstgen : copy First region generics only"
        print "                  frtbl  : copy Flash Region Table only"
        print "                  ccsd   : copy cCSD datas only"
        print "                  perfw  : copy PerFirmware datas only"
        print "                  cvtrm  : copy cVTRM datas only"
        print "                  secgen : copy Second region generics only"
        print " [input_file]  Original (corrupted) dump filename."
        print " [donnor_file] Donor (healthy) dump filename."
        print " [output_file] Saved generated filename (optional). If not defined, will be"
        print "               saved as \"[input_file].rebuilt.bin\" ."
        print
        print " Examples:"
        print "  %s all myCorruptedDump.bin healtyDonorDump.bin"%(os.path.basename(__file__))
        print "  %s cvtrm myCorruptedDump.bin healtyDonorDump.bin myRebuiltDump.bin"%(os.path.basename(__file__))

        sys.exit()

    startTime = time.time()


    # regions parameters
    d = {}

# NOR map:
    d["NOR_fstgen_offset"]    = 0x0
    d["NOR_fstgen_length"]    = 0x400
    d["NOR_frtbl_offset"]    = 0x400
    d["NOR_frtbl_length"]    = 0x400
    # d["NOR_metldr_offset"]    = 0x800       # PerConsole
    # d["NOR_metldr_length"]    = 0x2E800
    # d["NOR_eeid_offset"]    = 0x2F000     # PerConsole
    # d["NOR_eeid_length"]    = 0x10000
    # d["NOR_cisd_offset"]    = 0x3F000     # PerConsole
    # d["NOR_cisd_length"]    = 0x800
    d["NOR_ccsd_offset"]    = 0x3F800
    d["NOR_ccsd_length"]    = 0x800
    d["NOR_perfw_offset"]    = 0x40000
    d["NOR_perfw_length"]    = 0xE80000
    d["NOR_cvtrm_offset"]    = 0xEC0000
    d["NOR_cvtrm_length"]    = 0x40000
    d["NOR_secgen_offset"]    = 0xF00000
    d["NOR_secgen_length"]    = 0xC0000
    # d["NOR_bootldr_offset"]    = 0xFC0000     # PerConsole
    # d["NOR_bootldr_length"]    = 0x40000

# NAND map:
    # d["NAND_bootldr1_offset"]    = 0x0     # PerConsole
    # d["NAND_bootldr1_length"]    = 0x40000
    d["NAND_fstgen_offset"]        = 0x40000
    d["NAND_fstgen_length"]        = 0x200
    d["NAND_frtbl_offset"]        = 0x40200
    d["NAND_frtbl_length"]        = 0x600
    # d["NAND_metldr_offset"]        = 0x40800    # PerConsole
    # d["NAND_metldr_length"]        = 0x40000
    # d["NAND_eeid_offset"]        = 0x80800   # PerConsole
    # d["NAND_eeid_length"]        = 0x10000
    # d["NAND_cisd_offset"]        = 0x90800     # PerConsole
    # d["NAND_cisd_length"]        = 0x800
    d["NAND_ccsd_offset"]        = 0x91000
    d["NAND_ccsd_length"]        = 0x800
    d["NAND_perfw_offset"]        = 0x91800
    d["NAND_perfw_length"]        = 0xE2E800
    d["NAND_cvtrm_offset"]        = 0xEC0000
    d["NAND_cvtrm_length"]        = 0x40000
          # 0xF00000 - 0xEFFFFFF : Vflash area, PerConsole
    d["NAND_secgen_offset"]        = 0xE780000   # PerConsole ?
    d["NAND_secgen_length"]        = 0x880000
    # d["NAND_bootldr2_offset"]    = 0xF000000  # PerConsole
    # d["NAND_bootldr2_length"]    = 0x40000


    # cmdList = ["fstgen", "frtbl", "ccsd", "perfw", "cvtrm", "secgen"]
    cmdList = {"fstgen": "First region generics", "frtbl": "Flash Region Table", "ccsd": "cCSD", "perfw": "PerFirmware datas", "cvtrm": "cVTRM", "secgen": "Second region generics"}

    # get arguments:
    if len(sys.argv) <= 3 or sys.argv[1].lower() not in ["all", "all-", "fstgen", "frtbl", "ccsd", "perfw", "cvtrm", "secgen"]:
        sys.exit("ERROR: missing or wrong arguments. Run \"%s\" for help."%(os.path.basename(__file__)))
    else:
        cmd = sys.argv[1].lower()

    inputFile = sys.argv[2]
    if not os.path.isfile(inputFile):
        sys.exit("ERROR: input file \"%s\" not found!"%inputFile)

    donorFile = sys.argv[3]
    if not os.path.isfile(donorFile):
        sys.exit("ERROR: donor file \"%s\" not found!"%donorFile)

    if len(sys.argv) > 4:
        outputFile = sys.argv[4]
    else:
        outputFile = "%s.rebuilt.bin"%inputFile

    if inputFile == donorFile or inputFile == outputFile or donorFile == outputFile:
        sys.exit("ERROR: [input_file], [donnor_file] and [output_file] args must be different!")

    # parse file type:
    fileSize = os.path.getsize(inputFile)
    if fileSize == 16777216:
        inputFlashType = "NOR"
    elif fileSize == 268435456:
        inputFlashType = "NAND"
    else:
        print "ERROR: unable to define [input_file] flash type! (size doesn't match NOR/NAND)"
        quit()

    fileSize = os.path.getsize(donorFile)
    if fileSize == 16777216:
        donorFlashType = "NOR"
    elif fileSize == 268435456:
        donorFlashType = "NAND"
    else:
        print "ERROR: unable to define [donor_file] flash type! (size doesn't match NOR/NAND)"
        quit()

    if inputFlashType != donorFlashType:
        sys.exit("ERROR: [input_file] is a %s dump, [donnor_file] is a %s dump!"%(inputFlashType, donorFlashType))


    print "Flash type :", inputFlashType

    # check if bytes reversed dump:
    if inputFlashType == "NOR" and checkReversed(inputFile) == True:
        print "Input file reversed : YES"
        inputIsReversed = True
    elif inputFlashType == "NOR" and checkReversed(inputFile) == False:
        print "Input file reversed : NO"
        inputIsReversed = False
    else:
        inputIsReversed = False

    if donorFlashType == "NOR" and checkReversed(donorFile) == True:
        print "Donor file reversed : YES"
        donorIsReversed = True
    elif donorFlashType == "NOR" and checkReversed(donorFile) == False:
        print "Donor file reversed : NO"
        donorIsReversed = False
    else:
        donorIsReversed = False

    swap = inputIsReversed != donorIsReversed

    print

    # Copy input file to output file
    print "Copying input file to output file...",
    shutil.copyfile(inputFile, outputFile)
    print "done"

    # Verify copied file
    print "  Verifying copied output file...",
    if not getMD5(inputFile) == getMD5(outputFile):
        sys.exit("ERROR: copy verification failed!")
    print "done"

    # Execute command
    for c in cmdList.keys():
        if cmd == "all-" and c == "perfw":    # skip if true
            continue
        if cmd not in ["all", "all-"] and cmd != c:    # skip if true
            continue
        offset = "%s_%s_offset"%(inputFlashType, c)
        length = "%s_%s_length"%(inputFlashType, c)
        print "Copying %s from donor file to output file..."%cmdList[c],
        copyDatas(donorFile, outputFile, d[offset], d[length], swap)

    print
    print "Output file saved as \"%s\""%outputFile
    print "Done in %.2f seconds."%(time.time() - startTime)
    sys.exit()