#!/usr/bin/python
# -*- coding: utf-8 -*-

# *************************************************************************
# PyPS3patcher - Python patcher scypt for PS3 flash memory dump files
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
from xml.etree import ElementTree


def getFileBytes(file):
	f = open(file,"rb")
	bytes = f.read()
	f.close()
	return bytes

def getFileString(file):
	f = open(file,"r")
	string = f.readline()
	f.close()
	return string

def getMD5(file):
	h = hashlib.md5()
	f = open(file, "rb")
	h.update(f.read())
	f.close()
	return h.hexdigest()	

def checkMD5(file, md5):
	h = getMD5(file)
	return h == md5

def checkReversed(file):
	f = open(file,"rb")
	f.seek(0x200)
	bytes = f.read(0x4)
	f.close()
	if bytes == '\x49\x46\x49\x00':
		return False
	elif bytes == '\x46\x49\x00\x49':
		return True
	else:
		sys.exit("ERROR: unable to define if file %s is byte reversed! It doesn't seem to be a valid dump."%file)

def reverse(data):
	rev = ''.join([c for t in zip(data[1::2], data[::2]) for c in t])
	return rev

def writeBytesToFile(data, file):
	f = open(file,"wb")
	f.write(data)
	f.close

def patch(file, rospatch, rvk, type, rev):
	f = open(file,"r+b")
	if type == "NOR":
		if rev:
			rospatchdatas = reverse(getFileBytes(rospatch))
		else:
			rospatchdatas = getFileBytes(rospatch)
		f.seek(0xC0010)
		f.write(rospatchdatas)
		f.seek(0x7C0010)
		f.write(rospatchdatas)
		if rvk:
			global norRVK_patchFile
			f.seek(0x40000)
			if rev:
				f.write(reverse(getFileBytes(norRVK_patchFile)))
			else:
				f.write(getFileBytes(norRVK_patchFile))
	elif type == "NAND":
		f.seek(0xC0030)
		f.write(getFileBytes(rospatch))
		f.seek(0x7C0020)
		f.write(getFileBytes(rospatch))
		if rvk:
			global nandRVK_patchFile
			f.seek(0x91800)
			f.write(getFileBytes(nandRVK_patchFile))
	f.close

def verify (file, rospatch, rvk, type, rev):
	result = True
	f = open(file,"rb")
	if type == "NOR":
		if rev:
			rospatchdatas = reverse(getFileBytes(rospatch))
		else:
			rospatchdatas = getFileBytes(rospatch)
		f.seek(0xC0010)
		if not f.read(0x6FFFE0) == rospatchdatas:
			result = False
		f.seek(0x7C0010)
		if not f.read(0x6FFFE0) == rospatchdatas:
			result = False
		if rvk:
			global norRVK_patchFile
			f.seek(0x40000)
			if rev:
				if not f.read(0x80000) == reverse(getFileBytes(norRVK_patchFile)):
				 	result = False
			else:
				if not f.read(0x80000) == getFileBytes(norRVK_patchFile):
					result = False
	elif type == "NAND":
		f.seek(0xC0030)
		if not f.read(0x6FFFE0) == getFileBytes(rospatch):
			result = False
		f.seek(0x7C0020)
		if not f.read(0x6FFFE0) == getFileBytes(rospatch):
			result = False
		if rvk:
			global nandRVK_patchFile
			f.seek(0x91800)
			if not f.read(0x4000) == getFileBytes(nandRVK_patchFile):
				result = False
	return result
	f.close

def ending():
	global startTime
	global outputFile
	print
	print "Output file saved as \"%s\""%outputFile
	print "Done in %.2f seconds."%(time.time() - startTime)
	sys.exit()


if __name__ == "__main__":

	release = "v0.2"

	with open("patches/patches.info", "rt") as f:
		tree = ElementTree.parse(f)

	for node in tree.iter("patches"):
		nofsmROS_patchName = node.findtext("nofsm/name")

	print
	print "  ____        ____  ____ _____             _       _               "
	print " |  _ \ _   _|  _ \/ ___|___ / _ __   __ _| |_ ___| |__   ___ _ __ "
	print " | |_) | | | | |_) \___ \ |_ \| '_ \ / _` | __/ __| '_ \ / _ \ '__|"
	print " |  __/| |_| |  __/ ___) |__) | |_) | (_| | || (__| | | |  __/ |   "
	print " |_|    \__, |_|   |____/____/| .__/ \__,_|_| \___|_| |_|\___|_|   "
	print "        |___/                 |_|                            %s "%release
	print
	print "Python patcher scypt for PS3 flash memory dump files"
	print "Copyright (C) 2015 littlebalup@gmail.com"
	print
	if len(sys.argv) == 1:
		print "Usage:"
		print "%s [command] [input_file] [output_file]"%(os.path.basename(__file__))
		print
		print "  [command]      Command from list:"
		print "                    nofsm     : apply 4.XX noFSM ROS patches."
		print "                    nofsm_rvk : apply 4.XX noFSM ROS patches + RVK patches."
		print "                    fsm       : apply 3.55 FSM patches (ROS + RVK patches)."
		print "                    cust      : apply a custom ROS patches."
		print "                    cust_rvk  : apply a custom ROS patches + RVK patches."
		print "                    swap      : byte reverse."
		print "  [input_file]   Original dump filename."
		print "  [output_file]  Saved generated filename (optionnal). If not defined, will be"
		print "                 saved as \"[input_file].patched.bin\" for patch commands or as"
		print "                 \"[input_file].swaped.bin\" for swap command."
		print " NOTES :"
		print " - Embedded 4.XX noFSM ROS patch file is \"%s\"."%nofsmROS_patchName
		print " - Custom ROS patch file must be nammed \"patch.bin\" and located to the script"
		print "   folder."
		print
		print " Examples:"
		print "  %s nofsm mydump.bin"%(os.path.basename(__file__))
		print "  %s fsm mydump.bin mydump_patched.bin"%(os.path.basename(__file__))
		print "  %s cust_rvk D:\myfolder\mydump.bin"%(os.path.basename(__file__))
		sys.exit()

	startTime = time.time()

	# Set patches datas:
	for node in tree.iter("patches"):
		nofsmROS_patchName = node.findtext("nofsm/name")
		nofsmROS_patchMD5 = node.findtext("nofsm/hash")
		fsmROS_patchMD5 = node.findtext("fsm/hash")
		norRVK_patchMD5 = node.findtext("norRVK/hash")
		nandRVK_patchMD5 = node.findtext("nandRVK/hash")
	nofsmROS_patchFile = "patches/nofsm_patch.bin"
	fsmROS_patchFile = "patches/fsm_patch.bin"
	norRVK_patchFile = "patches/nor_rvk.bin"
	nandRVK_patchFile = "patches/nand_rvk.bin"

	# get arguments:
	if len(sys.argv) == 2 or sys.argv[1].lower() not in ["nofsm", "nofsm_rvk", "fsm", "cust", "cust_rvk", "swap"]:
		sys.exit("ERROR: missing or wrong arguments. Run \"%s\" for help."%(os.path.basename(__file__)))
	else:
		patchsType = sys.argv[1].lower()

	inputFile = sys.argv[2]
	if not os.path.isfile(inputFile):
		sys.exit("ERROR: input file \"%s\" was not found!"%inputFile)

	if len(sys.argv) > 3:
		outputFile = sys.argv[3]
	elif patchsType == "swap":
		outputFile = "%s.swapped.bin"%inputFile
	else:
		outputFile = "%s.patched.bin"%inputFile

	if inputFile == outputFile:
		sys.exit("ERROR: [input_file] and [output_file] arguments must be different!")

	# parse file type:
	fileSize = os.path.getsize(inputFile)
	if fileSize == 16777216:
		flashType = "NOR"
	elif fileSize == 268435456:
		flashType = "NAND"
	else:
		print "ERROR: unable to define flash type! It doesn't seem to be a valid dump."
		quit()
	print "Flash type :", flashType

	# check if bytes reversed dump:
	if flashType == "NOR" and checkReversed(inputFile) == True:
		print "Reversed : YES"
		isReversed = True
	elif flashType == "NOR" and checkReversed(inputFile) == False:
		print "Reversed : NO"
		isReversed = False
	else:
		isReversed = False

	# if swap command:
	if patchsType == "swap":
		print
		print "Reversing bytes from input file to output file...",
		writeBytesToFile(reverse(getFileBytes(inputFile)), outputFile)
		print "done"
		print "Verifying reversed output file...",
		h = hashlib.md5()
		h.update(reverse(getFileBytes(outputFile)))
		if not getMD5(inputFile) == h.hexdigest():
			sys.exit("ERROR: verification failed!")
		print "done"
		ending()

	# set patches and check integrity:
	print
	print "Checking integrity of patch files...",

	if patchsType == "fsm":
		if not os.path.isfile(fsmROS_patchFile):
			sys.exit("ERROR: patch file \"%s\" was not found!"%fsmROS_patchFile)
		elif not checkMD5(fsmROS_patchFile, fsmROS_patchMD5):
			sys.exit("ERROR: patch file \"%s\" seems corrupted!"%fsmROS_patchFile)
		ROSpatchFile = fsmROS_patchFile
	elif patchsType in ["nofsm", "nofsm_rvk"]:
		if not os.path.isfile(nofsmROS_patchFile):
			sys.exit("ERROR: patch file \"%s\" was not found!"%nofsmROS_patchFile)
		elif not checkMD5(nofsmROS_patchFile, nofsmROS_patchMD5):
			sys.exit("ERROR: patch file \"%s\" seems corrupted!"%nofsmROS_patchFile)
		ROSpatchFile = nofsmROS_patchFile
	else: # custom
		ROSpatchFile = "patch.bin"
		if not os.path.isfile(ROSpatchFile):
			sys.exit("ERROR: patch file \"%s\" was not found!"%ROSpatchFile)
		if not os.path.getsize(ROSpatchFile) == 7340000:
			sys.exit("ERROR: wrong size of patch file \"%s\" !"%ROSpatchFile)

	apply_rvk = patchsType in ["nofsm_rvk", "fsm", "cust_rvk"]

	if apply_rvk and flashType == "NOR":
		if not os.path.isfile(norRVK_patchFile):
			sys.exit("ERROR: patch file \"%s\" was not found!"%norRVK_patchFile)
		elif not checkMD5(norRVK_patchFile, norRVK_patchMD5):
			sys.exit("ERROR: patch file \"%s\" seems corrupted!"%norRVK_patchFile)
	elif apply_rvk and flashType == "NAND":
		if not os.path.isfile(nandRVK_patchFile):
			sys.exit("ERROR: patch file \"%s\" was not found!"%nandRVK_patchFile)
		elif not checkMD5(nandRVK_patchFile, nandRVK_patchMD5):
			sys.exit("ERROR: patch file \"%s\" seems corrupted!"%nandRVK_patchFile)

	print "done"

	# Copy input file to output file
	print "Copying input file to output file...",
	shutil.copyfile(inputFile, outputFile)
	print "done"

	# Verify copied file
	print "Verifying copied output file...",
	if not getMD5(inputFile) == getMD5(outputFile):
		sys.exit("ERROR: copy verification failed!")
	print "done"

	# apply patchs to output file:
	print "Applying patches to output file...",
	patch(outputFile, ROSpatchFile, apply_rvk, flashType, isReversed)
	print "done"

	# verify patchs application:
	print "Verifying patches application...",
	if not verify(outputFile, ROSpatchFile, apply_rvk, flashType, isReversed):
		sys.exit("ERROR: verification failed!")
	print "done"

	print
	print "All patches applied successfully!"

	#os.system("pause")

	ending()