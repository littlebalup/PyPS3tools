#!/usr/bin/python
# -*- coding: utf-8 -*-

# *************************************************************************
# PyPS3checker - Python checker script for PS3 flash memory dump files
#
# Copyright (C) 2015 littlebalup@gmail.com
#
# This code is licensed to you under the terms of the GNU GPL, version 2;
# see http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# *************************************************************************


import os
import time
import sys
import re
import hashlib
from xml.etree import ElementTree
from collections import Counter

try:
	from colorama import init, Fore, Back, Style
except ImportError:
	colorisok = False
else:
	colorisok = True
	init(autoreset=True)

class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)

def checkReversed(data):
	bytes = data[0x14:(0x14 + 0x4)]  # FACEOFF
	if bytes == '\x0F\xAC\xE0\xFF':
		return False
	elif bytes == '\xAC\x0F\xFF\xE0':
		return True
	bytes = data[0x1C:(0x1C + 0x4)]  # DEADBEEF
	if bytes == '\xDE\xAD\xBE\xEF':
		return False
	elif bytes == '\xAD\xDE\xEF\xBE':
		return True
	bytes = data[0x200:(0x200 + 0x4)]  # IFI
	if bytes == '\x49\x46\x49\x00':
		return False
	elif bytes == '\x46\x49\x00\x49':
		return True
	bytes = data[0x3F060:(0x3F060 + 0x4)]  # I.DL
	if bytes == '\x7F\x49\x44\x4C':
		return False
	elif bytes == '\x49\x7F\x4C\x44':
		return True
	bytes = data[0xF00014:(0xF00014 + 0x4)]  # FACEOFF
	if bytes == '\x0F\xAC\xE0\xFF':
		return False
	elif bytes == '\xAC\x0F\xFF\xE0':
		return True
	bytes = data[0xF0001C:(0xF0001C + 0x4)]  # DEADFACE
	if bytes == '\xDE\xAD\xFA\xCE':
		return False
	elif bytes == '\xAD\xDE\xCE\xFA':
		return True
	sys.exit("ERROR: unable to determine if reversed data! Too much curruptions.")
	
def isMetldr2(data):
	bytes = data[0x820:(0x820 + 0x8)]
	if bytes == '\x6D\x65\x74\x6C\x64\x72\x00\x00':   # METLDR
		return "false"
	elif bytes == '\x6D\x65\x74\x6C\x64\x72\x2E\x32':   # METLDR.2
		return "true"
	sys.exit("ERROR: unable to determine if NAND or EMMC data! Too much curruptions.")

def getDatas(file, offset, length):
	bytes = file[offset:(offset + length)]
	return bytes

def reverse(data):
	return ''.join([c for t in zip(data[1::2], data[::2]) for c in t])

def string2hex(data):
	return "".join("{:02x}".format(ord(c)) for c in data)

def hex2string(data):
    bytes = []
    for i in range(0, len(data), 2):
        bytes.append(chr(int(data[i:i+2], 16)))
    return ''.join(bytes)

def chunks(s, n):
	# Produce `n`-character chunks from `s`.
	for start in range(0, len(s), n):
		yield s[start:start+n]

def print_formatedlines(s, n):
	c = 0
	for chunk in chunks(s, n):
		if c == 0:
			tab = "   >"
		else:
			tab = "    "
		print tab, " ".join(a+b for a,b in zip(chunk[::2], chunk[1::2]))
		c += 1

def getMD5(file, offset, length):
	h = hashlib.md5()
	h.update(getDatas(file, offset, length))
	return h.hexdigest()

def printcolored(color, text):
	# available color: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
	# available style: DIM, NORMAL, BRIGHT, RESET_ALL
	# available back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
	if colorisok:
		COLOR = getattr(Fore, "%s"%color.upper())
		print(COLOR + Style.NORMAL + "%s"%text)
	else:
		print text

def colored(color, text):
	# available color: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
	# available style: DIM, NORMAL, BRIGHT, RESET_ALL
	# available back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
	if colorisok:
		COLOR = getattr(Fore, "%s"%color.upper())
		return COLOR + Style.NORMAL + "%s"%text
	else:
		return text

def printok(): print colored("green", "OK")

def printrisklevel(risklevel): 
	if risklevel == "WARNING": print colored("yellow", "%s!"%risklevel)
	if risklevel == "DANGER": print colored("red", "%s!"%risklevel)


if __name__ == "__main__":

	release = "v0.11.x"

	print
	print
	print
	printcolored("cyan", "  ____        ____  ____ _____      _               _             ")
	printcolored("cyan", " |  _ \ _   _|  _ \/ ___|___ /  ___| |__   ___  ___| | _____ _ __ ")
	printcolored("cyan", " | |_) | | | | |_) \___ \ |_ \ / __| '_ \ / _ \/ __| |/ / _ \ '__|")
	printcolored("cyan", " |  __/| |_| |  __/ ___) |__) | (__| | | |  __/ (__|   <  __/ |   ")
	printcolored("cyan", " |_|    \__, |_|   |____/____/ \___|_| |_|\___|\___|_|\_\___|_|   ")
	printcolored("cyan", "        |___/                                               %s "%release)
	print
	printcolored("white", " Python checker script for PS3 flash memory dump files")
	printcolored("cyan", " Copyright (C) 2015 littlebalup@gmail.com")
	print
	print
	if len(sys.argv) == 1:
		print "Usage:"
		print "%s [input_file]"%os.path.basename(sys.argv[0])
		print
		print " [input_file]   Dump filename to check."
		print
		print " Examples:"
		print "  %s mydump.bin"%os.path.basename(sys.argv[0])
		sys.exit()


	startTime = time.time()

	# get args and set recording lists and counts
	inputFile = sys.argv[1]
	if not os.path.isfile(inputFile):
		sys.exit("ERROR: input file \"%s\" not found!"%inputFile)

	dangerList = []
	warningList = []
	checkCount = 0
	dangerCount = 0
	warningCount = 0
	
	skipHash = False

	# parse file
	print "Loading file \"%s\" to memory..."%inputFile,
	f = open(inputFile,"rb")
	rawfiledata = f.read()
	f.close()
	# parse xml
	if not os.path.isfile("checklist.xml"):
		sys.exit("ERROR: checklist.xml file not found!")
	if not os.path.isfile("hashlist.xml"):
		sys.exit("ERROR: hashlist.xml file not found!")
	with open('checklist.xml', 'rt') as f:
		chktree = ElementTree.parse(f)
	with open('hashlist.xml', 'rt') as f:
		hashtree = ElementTree.parse(f)

	# parse file type:
	isReversed = ""
	fileSize = len(rawfiledata)
	flashType = ""
	for dump_type in chktree.findall('.//dump_type'):
		if fileSize == int(dump_type.attrib.get("size")):
			if dump_type.attrib.get("metldr2") is not None:
				if isMetldr2(rawfiledata) != dump_type.attrib.get("metldr2").lower():
					continue
			if dump_type.attrib.get("chk_rev") == "true":
				if checkReversed(rawfiledata) == True:
					isReversed = True
					rawfiledata = reverse(rawfiledata)
				else:
					isReversed = False
			flashType =  dump_type.attrib.get("name")
			flashText = dump_type.text
			break
	if flashType == "":
			print
			sys.exit("ERROR: unable to determine flash type! It doesn't seem to be a valid dump.")

	print " Done"

	# create and start log
	cl = open('%s.checklog.txt'%inputFile, 'w')
	cl.write("PyPS3checker %s. Check log.\n\n"%release + "Checked file : %s\n"%inputFile)
	# original = sys.stdout
	sys.stdout = Tee(sys.stdout, cl)

	print
	print
	print "******* Getting flash type *******"
	print "  Flash type :", flashText
	if isReversed == True:
		print "  Reversed : YES"
	elif isReversed == False:
		print "  Reversed : NO"


	# SKU identification
	print
	print
	print "******* Getting SKU identification datas *******"
	skufiledata = {}
	for entry in chktree.findall('.//%s/skulistdata/'%flashType):
		filedata = string2hex(getDatas(rawfiledata, int(entry.attrib.get("offset"), 16), int(entry.attrib.get("size"), 16)))
		tag = entry.text
		if tag == "bootldrsize":
			calc = (int(filedata, 16) * 0x10) + 0x40
			filedata = "%X"%calc
		skufiledata[tag] = filedata.lower()
		if tag == "idps":
			print "  %s = 0x%s"%(tag, filedata[-2:].upper())  #print only last 2 digits
		else:
			print "  %s = 0x%s"%(tag, filedata.upper())
	print
	print "  Matching SKU :",
	checkCount += 1
	ChkResult = False
	for node in chktree.findall('.//%s/skumodels'%flashType):
		risklevel = node.attrib.get("risklevel").upper()
	for node in chktree.findall('.//%s/skumodels/'%flashType):
		d = {}
		for subnode in chktree.findall(".//%s/skumodels/%s[@id='%s']/"%(flashType, node.tag, node.attrib.get("id"))):
			tag = subnode.attrib.get("type")
			d[tag] = subnode.text.lower()
		if d == skufiledata:
			ChkResult = True
			printok()
			print "   %s"%node.attrib.get("name")
			print "   Minimum version %s"%node.attrib.get("minver")
			if node.attrib.get("warn") == "true":
				warningCount += 1
				warningList.append("SKU identification")
				print colored("yellow", " %s"%node.attrib.get("warnmsg"))
			break
	if ChkResult == False:
		if risklevel == "DANGER":
			dangerCount += 1
			dangerList.append("SKU identification")
		elif risklevel == "WARNING":
			warningCount += 1
			warningList.append("SKU identification")
		printrisklevel(risklevel)
		print "   No matching SKU found!"

	# SDK vesrions
	print
	print
	print "******* Getting SDK versions *******"
	checkCount += 1
	ChkResult = True
	for node in chktree.findall('.//%s/sdk'%flashType):
		risklevel = node.attrib.get("risklevel").upper()
	for sdk in chktree.findall('.//%s/sdk/sdk_version'%flashType):
		index = rawfiledata.find(hex2string("73646B5F76657273696F6E"), int(sdk.attrib.get("offset"), 16), int(sdk.attrib.get("offset"), 16) + 0x4f0)
		addressPos = index - 0xc
		address = int(sdk.attrib.get("offset"), 16) + int(string2hex(getDatas(rawfiledata, addressPos, 0x4)), 16)
		ver = getDatas(rawfiledata, address, 0x8)
		ver = ver[:-1]                       #remove useless last 0x0A char   
		r = re.compile('\d{3}\.\d{3}')         #def format 
		if r.match(ver) is not None:
			print "  %s : %s"%(sdk.attrib.get("name"), ver)
		else:
			print "  %s : (unknown)"%(sdk.attrib.get("name"))
			ChkResult = False
	if ChkResult == False:
		if risklevel == "DANGER":
			dangerCount += 1
			dangerList.append("SDK versions")
		elif risklevel == "WARNING":
			warningCount += 1
			warningList.append("SDK versions")
		print "%s! : unable to get all versions."%risklevel

	# Start other checks
	for node in chktree.findall('.//%s/'%flashType):
		if node.tag not in ["skulistdata", "skumodels", "sdk"]:
			print
			print
			print "******* Checking %s *******"%node.tag

		for subnode in chktree.findall('.//%s/%s/'%(flashType, node.tag)):
			if subnode.attrib.get("risklevel") is not None:
				risklevel = subnode.attrib.get("risklevel").upper()

			if subnode.tag == "binentry":
				checkCount += 1
				filedata = string2hex(getDatas(rawfiledata, int(subnode.attrib.get("offset"), 16), len(subnode.text)/2))
				print "%s :"%subnode.attrib.get("name"),
				if filedata.lower() == subnode.text.lower():
					printok()
				else:
					if risklevel == "DANGER":
						dangerCount += 1
						dangerList.append(subnode.attrib.get("name"))
					elif risklevel == "WARNING":
						warningCount += 1
						warningList.append(subnode.attrib.get("name"))
					printrisklevel(risklevel)
					print "  At offset : 0x%s"%subnode.attrib.get("offset").upper()
					if isReversed:
						print "  Actual data (reversed from original) :"
					else:
						print "  Actual data :"
					print_formatedlines(filedata.upper(), 32)
					print "  Expected data :"
					print_formatedlines(subnode.text.upper(), 32)
					print

			if subnode.tag == "multibinentry":
				checkCount += 1
				ChkResult = False
				filedata = string2hex(getDatas(rawfiledata, int(subnode.attrib.get("offset"), 16), int(subnode.attrib.get("length"), 16)))
				print "%s :"%subnode.attrib.get("name"),
				for entry in chktree.findall(".//%s/%s/%s[@name='%s']/"%(flashType, node.tag, subnode.tag, subnode.attrib.get("name"))):
					if filedata.lower() == entry.text.lower():
						if subnode.attrib.get("name").endswith("trvk_prg1 SCE") and entry.text == "FFFFFFFF" :
							print "Blank"
							skipHash = True
						elif subnode.attrib.get("name").endswith("trvk_pkg1 SCE") and entry.text == "FFFFFFFF" :
							print "Blank"
						else:
							printok()
						ChkResult = True
						break
				if ChkResult == False:
					if risklevel == "DANGER":
						dangerCount += 1
						dangerList.append(subnode.attrib.get("name"))
					elif risklevel == "WARNING":
						warningCount += 1
						warningList.append(subnode.attrib.get("name"))
					printrisklevel(risklevel)
					print "  At offset : 0x%s"%subnode.attrib.get("offset").upper()
					if isReversed:
						print "  Actual data (reversed from original) :"
					else:
						print "  Actual data :"
					print_formatedlines(filedata.upper(), 32)
					print "  Expected data (one of the list):"
					for entry in chktree.findall(".//%s/%s/%s[@name='%s']/"%(flashType, node.tag, subnode.tag, subnode.attrib.get("name"))):
						print_formatedlines(entry.text.upper(), 32)
					print
						
			if subnode.tag == "datafill":
				checkCount += 1
				ChkResult = True
				print "%s :"%subnode.attrib.get("name"),
				if subnode.attrib.get("ldrsize") is not None:
					ldrsize = (int(string2hex(getDatas(rawfiledata, int(subnode.attrib.get("ldrsize"), 16), 0x2)), 16) * 0x10) + 0x40
					start = int(subnode.attrib.get("regionstart"), 16) + ldrsize
					length = int(subnode.attrib.get("regionsize"), 16) - ldrsize
				elif subnode.attrib.get("sizefrom") is not None:
					datasize = int(string2hex(getDatas(rawfiledata, int(subnode.attrib.get("sizefrom"), 16), 0x2)), 16)
					start = int(subnode.attrib.get("regionstart"), 16) + datasize
					length = int(subnode.attrib.get("regionsize"), 16) - datasize
				else:
					start = int(subnode.attrib.get("offset"), 16)
					length = int(subnode.attrib.get("size"), 16)
				filedata = getDatas(rawfiledata, start, length)
				c = 0
				for data in filedata:
					b = string2hex(data)
					if b.lower() != subnode.text.lower():
						ChkResult = False
						FalseOffset = start + c
						FalseValue = b
						break
					c += 1
				f.close()
				if ChkResult:
					printok()
				else:
					if risklevel == "DANGER":
						dangerCount += 1
						dangerList.append(subnode.attrib.get("name"))
					elif risklevel == "WARNING":
						warningCount += 1
						warningList.append(subnode.attrib.get("name"))
					printrisklevel(risklevel)
					print "  All bytes from offset 0x%X to offset 0x%X should be 0x%s."%(start, start + length, subnode.text.upper())
					print "  Byte at offset 0x%X has value : 0x%s"%(FalseOffset, FalseValue.upper())
					print "  Subsequent bytes in the range may be wrong as well."
					print

			if subnode.tag == "hash":
				checkCount += 1
				ChkResult = False
				print "%s :"%subnode.attrib.get("name"),
				if subnode.attrib.get("name").endswith("trvk_prg1 Hash") and skipHash:
					checkCount -= 1
					print "Skipped"
					continue
				if subnode.attrib.get("sizeoffset") is not None:
					size = int(string2hex(getDatas(rawfiledata, int(subnode.attrib.get("sizeoffset"), 16), int(subnode.attrib.get("sizelength"), 16))), 16)
				else:
					size = int(subnode.attrib.get("size"), 16)
				hashdata = getMD5(rawfiledata, int(subnode.attrib.get("offset"), 16), size)
				for hash in hashtree.findall(".//type[@name='%s']/"%(subnode.attrib.get("type"))):
					if hashdata.lower() == hash.text.lower():
						printok()
						ChkResult = True
						print "  Size = 0x%X"%size
						print "  MD5 =", hashdata.upper()
						print "  Version =", hash.attrib.get("name")
						break
				if ChkResult == False:
					if risklevel == "DANGER":
						dangerCount += 1
						dangerList.append(subnode.attrib.get("name"))
					elif risklevel == "WARNING":
						warningCount += 1
						warningList.append(subnode.attrib.get("name"))
					printrisklevel(risklevel)
					print "  Size = 0x%X"%size
					print "  MD5 =", hashdata.upper()
					print "  Version = (unknown)"
				print

			if subnode.tag == "datalist":
				print "%s :"%subnode.attrib.get("name"),
				if subnode.attrib.get("ldrsize") is not None:
					d = string2hex(getDatas(rawfiledata, int(subnode.attrib.get("ldrsize"), 16), 0x2))
					size = (int(d, 16) * 0x10) + 0x40
				else:
					size = int(subnode.attrib.get("size"), 16)
				filedata = getDatas(rawfiledata, int(subnode.attrib.get("offset"), 16), size)
				for datatreshold in chktree.findall(".//%s/%s/%s[@name='%s']/"%(flashType, node.tag, subnode.tag, subnode.attrib.get("name"))):
					checkCount += 1
					ChkResult = True
					r = {}
					if datatreshold.attrib.get("key") == "*":
						for k,v in Counter(filedata).items():
							c = float(v) / size * 100
							if c > float(datatreshold.text.replace(',','.')):
								ChkResult = False
								tag = string2hex(k).upper()
								r[tag] = c
					else:
						c = float(filedata.count(chr(int(datatreshold.attrib.get("key"), 16)))) / size * 100
						if c > float(datatreshold.text.replace(',','.')):
							tag = datatreshold.attrib.get("key").upper()
							r[tag] = c
					if ChkResult:
						printok()
					else:
						if risklevel == "DANGER":
							dangerCount += 1
							dangerList.append(subnode.attrib.get("name"))
						elif risklevel == "WARNING":
							warningCount += 1
							warningList.append(subnode.attrib.get("name"))
						printrisklevel(risklevel)
						if datatreshold.attrib.get("key") == "*":
							print "  Any bytes",
						else:
							print "  0x%s bytes"%datatreshold.attrib.get("key").upper(),
						print "from offset 0x%s to offset 0x%X should be less than %s%%."%(subnode.attrib.get("offset").upper(), int(subnode.attrib.get("offset"), 16) + size, datatreshold.text.replace(',','.'))
						for x in sorted(r.keys()):
							print "    0x%s is %.2f%%"%((x), r[x])

			if subnode.tag == "datamatchid":
				print subnode.text, ":",
				d = {}
				for id in chktree.findall(".//%s/%s//datamatch[@id='%s']"%(flashType, node.tag, subnode.attrib.get("id"))):
					checkCount += 1
					if id.attrib.get("seqrep") is not None:
						c = 0
						while c != int(id.attrib.get("seqrep"), 16):
							filedata = string2hex(getDatas(rawfiledata, int(id.attrib.get("offset"), 16) + c * int(id.attrib.get("length"), 16), int(id.attrib.get("length"), 16)))
							tag = "%s at 0x%X"%(id.text, int(id.attrib.get("offset"), 16) + c * int(id.attrib.get("length"), 16))
							d[tag] = filedata.upper()
							c += 1
					else:
						filedata = string2hex(getDatas(rawfiledata, int(id.attrib.get("offset"), 16), int(id.attrib.get("length"), 16)))
						tag = id.text
						d[tag] = filedata.upper()
				if len(set(d.values())) != 1:
					if risklevel == "DANGER":
						dangerCount += 1
						dangerList.append("datamatches : %s"%subnode.text)
					elif risklevel == "WARNING":
						warningCount += 1
						warningList.append("datamatches : %s"%subnode.text)
					printrisklevel(risklevel)
					print "  Following datas should be the same :"
					for id in chktree.findall(".//%s/%s//datamatch[@id='%s']"%(flashType, node.tag, subnode.attrib.get("id"))):
						if id.attrib.get("nodisp") is not None:
							print "  %s at offset 0x%s length 0x%s"%(id.text, id.attrib.get("offset").upper(), id.attrib.get("length").upper())
							print "    (too long to dilplay)"
						elif id.attrib.get("seqrep") is not None:
							print "  %s at offset 0x%s length 0x%s, repeted 0x%s time"%(id.text, id.attrib.get("offset").upper(), id.attrib.get("length").upper(), id.attrib.get("seqrep").upper())
							print "    (too long to dilplay)"
						else:
							print "  %s at offset 0x%s length 0x%s"%(id.text, id.attrib.get("offset").upper(), id.attrib.get("length").upper())
							print_formatedlines(d[id.text], 32)
					print
				else:
					printok()

			if subnode.tag == "repcheck":
				checkCount += 1
				ChkResult = True
				print "%s :"%subnode.attrib.get("name"),
				key = hex2string(subnode.text)
				beg = 0
				index = beg
				nothing = True
				indexlist = []
				while index != -1:
					index = rawfiledata.find(key, beg)
					if index != -1 and index != int(subnode.attrib.get("offset"), 16):
						nothing = False
						ChkResult = False
						indexlist.append("0x%X"%index)
					elif index == int(subnode.attrib.get("offset"), 16):
						nothing = False
					beg = index + (len(subnode.text) / 2)
				if nothing or not ChkResult:
					if risklevel == "DANGER":
						dangerCount += 1
						dangerList.append("repcheck : %s"%subnode.attrib.get("name"))
					elif risklevel == "WARNING":
						warningCount += 1
						warningList.append("repcheck : %s"%subnode.attrib.get("name"))
					printrisklevel(risklevel)
					if isReversed:
						print "  Following data (reversed) expected at offset 0x%s :"%subnode.attrib.get("offset").upper()
					else:
						print "  Following data expected at offset 0x%s :"%subnode.attrib.get("offset").upper()
					print_formatedlines(subnode.text, 32)
					if nothing:
						print "    No matching data found!"
						print
					else:
						print "  Repetition(s) found at offset(s) :"
						print "   ", ", ".join(indexlist)
						print
				else:
					printok()


	print
	print
	print "******* Additional information *******"
	if flashType == "NOR":
		HDD = getDatas(rawfiledata, 0xF20204, 0x3C)
		MAC = string2hex(getDatas(rawfiledata, 0x3F040, 0x6)).upper()
		CID = string2hex(getDatas(rawfiledata, 0x3F06A, 0x6)).upper()
		eCID = getDatas(rawfiledata, 0x3F070, 0x20)
		board_id = getDatas(rawfiledata, 0x3F090, 0x8)
		kiban_id = getDatas(rawfiledata, 0x3F098, 0xC)
		print "HDD :", " ".join(HDD.split())
	if flashType == "NAND":
		MAC = string2hex(getDatas(rawfiledata, 0x90840, 0x6)).upper()
		CID = string2hex(getDatas(rawfiledata, 0x9086A, 0x6)).upper()
		eCID = getDatas(rawfiledata, 0x90870, 0x20)
		board_id = getDatas(rawfiledata, 0x90890, 0x8)
		kiban_id = getDatas(rawfiledata, 0x90898, 0xC)
	if flashType in ['NAND_PS3Xploit', 'EMMC_PS3Xploit'] :
		MAC = string2hex(getDatas(rawfiledata, 0x90840-0x40000, 0x6)).upper()
		CID = string2hex(getDatas(rawfiledata, 0x9086A-0x40000, 0x6)).upper()
		eCID = getDatas(rawfiledata, 0x90870-0x40000, 0x20)
		board_id = getDatas(rawfiledata, 0x90890-0x40000, 0x8)
		kiban_id = getDatas(rawfiledata, 0x90898-0x40000, 0xC)
	print "MAC address :", ":".join(a+b for a,b in zip(MAC[::2], MAC[1::2]))
	print "CID : 0x%s"%CID
	print "eCID : %s"%eCID
	print "board_id (part of console S/N) : %s"%board_id
	print "kiban_id (board barcode) : %s"%kiban_id
	
	if CID.startswith("0FFF"): print colored("cyan", "This is a refurbished console!")
	
	print
	print
	print
	print "******* Checks completed *******"
	print
	print "Total number of checks =", checkCount
	print "Number of dangers =",
	if dangerCount > 0: print colored("red", dangerCount)
	else: print colored("green", dangerCount)
	print "Number of warnings =",
	if warningCount > 0: print colored("yellow", warningCount)
	else: print colored("green", warningCount)

	if dangerCount > 0:
		print
		print "Following check(s) returned a",
		printrisklevel("DANGER")
		print colored("red", "  " + "\n  ".join(dangerList))
		
	if warningCount > 0:
		print
		print "Following check(s) returned a",
		printrisklevel("WARNING")
		print colored("yellow", "  " + "\n  ".join(warningList))

	print
	print "All checks done in %.2f seconds."%(time.time() - startTime)
	
	if flashType in ['NOR', 'EMMC_PS3Xploit'] :
		print colored("MAGENTA", "\n\n\
 ---------------------------------------------------------------------------- \n\
| IMPORTANT NOTICE !                                                         |\n\
| Checks of late CECH-25xxx, CECH-3xxxx and CECH-4xxxx consoles dumps still  |\n\
| under development and may return false results. If you feel it's the case, |\n\
| please post your *.checklog.txt in a new issue on my github repository:    |\n\
|   https://github.com/littlebalup/PyPS3tools/issues                         |\n\
| Thanks! It will help me a lot to improve that tool ;)                      |\n\
 ---------------------------------------------------------------------------- ")
	

	cl.close()
	with open('%s.checklog.txt'%inputFile) as f:
		cleanlog = f.read().replace('\x1B\x5B\x33\x31\x6D\x1B\x5B\x32\x32\x6D', '')
		cleanlog = cleanlog.replace('\x1B\x5B\x33\x32\x6D\x1B\x5B\x32\x32\x6D', '')
		cleanlog = cleanlog.replace('\x1B\x5B\x33\x33\x6D\x1B\x5B\x32\x32\x6D', '')
		cleanlog = cleanlog.replace('\x1B\x5B\x33\x35\x6D\x1B\x5B\x32\x32\x6D', '')
	with open('%s.checklog.txt'%inputFile, "w") as f:
		f.write(cleanlog)
	

	if dangerCount > 0:
		sys.exit(3)
	elif warningCount > 0:
		sys.exit(2)
	else:
		sys.exit()
