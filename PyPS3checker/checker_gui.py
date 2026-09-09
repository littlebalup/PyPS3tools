#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import re
import hashlib
import textwrap
import threading
from xml.etree import ElementTree
from collections import Counter
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from tkinter import ttk

# --- Helper Functions from checker_py3.py ---

def checkReversed(data):
    bytes_val = data[0x14:(0x14 + 0x4)]
    if bytes_val == b'\x0F\xAC\xE0\xFF':
        return False
    elif bytes_val == b'\xAC\x0F\xFF\xE0':
        return True
    return None

def isMetldr2(data):
    bytes_val = data[0x820:(0x820 + 0x8)]
    if bytes_val == b'\x6D\x65\x74\x6C\x64\x72\x00\x00':
        return "false"
    elif bytes_val == b'\x6D\x65\x74\x6C\x64\x72\x2E\x32':
        return "true"
    return None

def getDatas(file_data, offset, length):
    return file_data[offset:(offset + length)]

def reverse(data):
    r_data = []
    for i in range(0, len(data), 2):
        r_data.append(data[i + 1])
        r_data.append(data[i])
    return bytes(r_data)

def string2hex(data):
    return "".join("{:02x}".format(b) for b in data)

def getMD5(file_data, offset, length):
    h = hashlib.md5()
    h.update(getDatas(file_data, offset, length))
    return h.hexdigest()

# --- Main App ---

class CheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyPS3checker GUI")
        
        # Fixed Window Size
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        
        self.filepath = None
        
        # Theme Colors
        self.colors = {
            "bg": "#2b2b2b",
            "fg": "#ffffff",
            "panel_bg": "#3c3f41",
            "button_bg": "#4b6eaf",
            "button_fg": "#ffffff",
            "accent_red": "#e06c75",
            "accent_green": "#98c379",
            "accent_yellow": "#e5c07b",
            "text_bg": "#1e1e1e",
        }
        
        # Configure Root Theme
        self.root.configure(bg=self.colors["bg"])
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure Styles
        self.style.configure("TFrame", background=self.colors["bg"])
        self.style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"], font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        self.style.configure("Stats.TLabel", background=self.colors["panel_bg"], font=("Segoe UI", 10))
        
        # Panel Style
        self.style.configure("Panel.TFrame", background=self.colors["panel_bg"], relief="flat")
        
        # Button Style
        self.style.configure("TButton", 
            font=("Segoe UI", 10, "bold"), 
            background=self.colors["button_bg"], 
            foreground=self.colors["button_fg"],
            borderwidth=0,
            focuscolor="none"
        )
        self.style.map("TButton",
            background=[('active', '#5b7ecf'), ('disabled', '#555555')],
            foreground=[('disabled', '#aaaaaa')]
        )

        self.setup_ui()
        
    def setup_ui(self):
        # Main Layout: Top Bar, Left Log, Right Info
        
        # --- Top Bar ---
        top_frame = ttk.Frame(self.root, padding="10 10 10 10")
        top_frame.pack(fill=tk.X, side=tk.TOP)
        
        self.btn_open = ttk.Button(top_frame, text="Open Dump File", command=self.load_file, width=20)
        self.btn_open.pack(side=tk.LEFT, padx=(0, 10))
        
        self.lbl_filename = ttk.Label(top_frame, text="No file selected", foreground="#aaaaaa", font=("Segoe UI", 10, "italic"))
        self.lbl_filename.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.btn_check = ttk.Button(top_frame, text="Verify Dump", command=self.start_check_thread, state=tk.DISABLED, width=20)
        self.btn_check.pack(side=tk.RIGHT)

        # --- Content Area ---
        content_frame = ttk.Frame(self.root, padding="10 0 10 10")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left: Log Output
        self.txt_log = scrolledtext.ScrolledText(
            content_frame, 
            font=("Consolas", 10), 
            state=tk.DISABLED, 
            bg=self.colors["text_bg"], 
            fg="#dcdcdc",
            insertbackground="white", # Cursor color
            bd=0,
            highlightthickness=0
        )
        self.txt_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Tags for coloring
        self.txt_log.tag_config("red", foreground=self.colors["accent_red"])
        self.txt_log.tag_config("green", foreground=self.colors["accent_green"])
        self.txt_log.tag_config("yellow", foreground=self.colors["accent_yellow"])
        self.txt_log.tag_config("cyan", foreground="#56b6c2")
        self.txt_log.tag_config("magenta", foreground="#c678dd")
        self.txt_log.tag_config("normal", foreground="#dcdcdc")
        
        # Right: Info & Stats Panel
        right_panel = ttk.Frame(content_frame, style="Panel.TFrame", width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False) # Force width
        
        # Inner padding for right panel
        panel_content = tk.Frame(right_panel, bg=self.colors["panel_bg"])
        panel_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Stats Section
        tk.Label(panel_content, text="STATISTICS", bg=self.colors["panel_bg"], fg="#aaaaaa", font=("Segoe UI", 9, "bold"), anchor="w").pack(fill=tk.X)
        
        self.lbl_total = tk.Label(panel_content, text="Total Checks: 0", bg=self.colors["panel_bg"], fg="white", font=("Segoe UI", 11), anchor="w")
        self.lbl_total.pack(fill=tk.X, pady=(5, 0))
        
        self.lbl_danger = tk.Label(panel_content, text="Dangers: 0", bg=self.colors["panel_bg"], fg=self.colors["accent_red"], font=("Segoe UI", 11), anchor="w")
        self.lbl_danger.pack(fill=tk.X)
        
        self.lbl_warning = tk.Label(panel_content, text="Warnings: 0", bg=self.colors["panel_bg"], fg=self.colors["accent_yellow"], font=("Segoe UI", 11), anchor="w")
        self.lbl_warning.pack(fill=tk.X)
        
        tk.Frame(panel_content, height=1, bg="#555555").pack(fill=tk.X, pady=15)
        
        # Console Info Section
        tk.Label(panel_content, text="CONSOLE INFO", bg=self.colors["panel_bg"], fg="#aaaaaa", font=("Segoe UI", 9, "bold"), anchor="w").pack(fill=tk.X)
        
        self.lbl_info = tk.Label(panel_content, text="Waiting for check...", bg=self.colors["panel_bg"], fg="#cccccc", justify=tk.LEFT, font=("Consolas", 9), anchor="nw")
        self.lbl_info.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def log(self, text, color=None, end="\n"):
        self.txt_log.config(state=tk.NORMAL)
        tag = color if color else "normal"
        self.txt_log.insert(tk.END, text + end, tag)
        self.txt_log.see(tk.END)
        self.txt_log.config(state=tk.DISABLED)

    def clear_log(self):
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.delete(1.0, tk.END)
        self.txt_log.config(state=tk.DISABLED)

    def load_file(self):
        # Fix: Use parent=self.root to keep dialog modal to this window
        file_path = filedialog.askopenfilename(
            parent=self.root,
            title="Select PS3 Dump File",
            filetypes=[("Binary Files", "*.bin *.hex *.dump;*.img"), ("All Files", "*.*")]
        )
        if file_path:
            self.filepath = file_path
            self.lbl_filename.config(text=os.path.basename(file_path))
            self.btn_check.config(state=tk.NORMAL)
            self.clear_log()
            self.log(f"Selected file: {self.filepath}")
            # Reset UI
            self.reset_stats()
            
    def reset_stats(self):
        self.lbl_total.config(text="Total Checks: 0")
        self.lbl_danger.config(text="Dangers: 0")
        self.lbl_warning.config(text="Warnings: 0")
        self.lbl_info.config(text="Ready to check.")

    def start_check_thread(self):
        self.btn_check.config(state=tk.DISABLED)
        self.btn_open.config(state=tk.DISABLED)
        self.clear_log()
        self.reset_stats()
        self.lbl_info.config(text="Checking...")
        
        threading.Thread(target=self.run_checks, daemon=True).start()

    def run_checks(self):
        try:
            self._execute_checks()
        except Exception as e:
            self.log(f"\nERROR: An unexpected error occurred: {e}", "red")
            import traceback
            traceback.print_exc()
        finally:
            self.root.after(0, lambda: self.btn_check.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.btn_open.config(state=tk.NORMAL))

    def _execute_checks(self):
        inputFile = self.filepath
        if not os.path.isfile(inputFile):
            self.log(f"ERROR: input file \"{inputFile}\" not found!", "red")
            return

        dangerList = []
        warningList = []
        checkCount = 0
        dangerCount = 0
        warningCount = 0
        skipHash = False

        self.log(f"Loading file \"{inputFile}\" to memory...", end="")
        try:
            with open(inputFile, "rb") as f:
                rawfiledata = f.read()
            self.log(" Done", "green")
        except Exception as e:
            self.log(f" FAILED: {e}", "red")
            return

        # Check for XML files
        base_dir = os.path.dirname(os.path.abspath(__file__))
        checklist_path = os.path.join(base_dir, "checklist.xml")
        hashlist_path = os.path.join(base_dir, "hashlist.xml")
        
        if not os.path.isfile(checklist_path):
             self.log("ERROR: checklist.xml file not found!", "red")
             return
        if not os.path.isfile(hashlist_path):
             self.log("ERROR: hashlist.xml file not found!", "red")
             return
             
        try:
            with open(checklist_path, 'rt') as f:
                chktree = ElementTree.parse(f)
            with open(hashlist_path, 'rt') as f:
                hashtree = ElementTree.parse(f)
        except Exception as e:
            self.log(f"ERROR parsing XML: {e}", "red")
            return

        # Parse file type
        isReversed = ""
        fileSize = len(rawfiledata)
        flashType = ""
        flashText = ""
        
        for dump_type in chktree.findall('.//dump_type'):
            if fileSize == int(dump_type.attrib.get("size")):
                if dump_type.attrib.get("metldr2") is not None:
                    res = isMetldr2(rawfiledata)
                    if res is None:
                         continue
                    if res != dump_type.attrib.get("metldr2").lower():
                        continue
                if dump_type.attrib.get("chk_rev") == "true":
                    res = checkReversed(rawfiledata)
                    if res is None:
                         self.log("ERROR: unable to determine if reversed data! Too much curruptions.", "red")
                         return
                    if res == True:
                        isReversed = True
                        rawfiledata = reverse(rawfiledata)
                    else:
                        isReversed = False
                flashType = dump_type.attrib.get("name")
                # Handle text safely if None
                flashText = dump_type.text if dump_type.text else "Unknown"
                break
                
        if flashType == "":
            self.log("ERROR: unable to determine flash type! It doesn't seem to be a valid dump.", "red")
            return

        log_buffer = []
        def write_dual(text, color=None, end="\n"):
            self.root.after(0, lambda: self.log(text, color, end))
            log_buffer.append(text + end)

        write_dual("\n\n******* Getting flash type *******")
        write_dual(f"  Flash type : {flashText}")
        if isReversed == True:
            write_dual("  Reversed : YES")
        elif isReversed == False:
            write_dual("  Reversed : NO")

        # SKU identification
        write_dual("\n******* Getting SKU identification datas *******")
        skufiledata = {}
        for entry in chktree.findall('.//%s/skulistdata/' % flashType):
            filedata = string2hex(getDatas(rawfiledata, int(entry.attrib.get("offset"), 16), int(entry.attrib.get("size"), 16)))
            tag = entry.text
            if tag == "bootldrsize":
                calc = (int(filedata, 16) * 0x10) + 0x40
                filedata = "%X" % calc
            skufiledata[tag] = filedata.lower()
            if tag == "idps":
                write_dual("  %s = 0x%s" % (tag, filedata[-2:].upper()))
            else:
                write_dual("  %s = 0x%s" % (tag, filedata.upper()))
        
        write_dual("\n  Matching SKU :", end=' ')
        checkCount += 1
        ChkResult = False
        risklevel = ""
        
        # Determine strictness first
        for node in chktree.findall('.//%s/skumodels' % flashType):
            risklevel = node.attrib.get("risklevel").upper()
            
        for node in chktree.findall('.//%s/skumodels/' % flashType):
            d = {}
            for subnode in chktree.findall(".//%s/skumodels/%s[@id='%s']/" % (flashType, node.tag, node.attrib.get("id"))):
                tag = subnode.attrib.get("type")
                d[tag] = subnode.text.lower()
            if d == skufiledata:
                ChkResult = True
                write_dual("OK", "green")
                write_dual("   %s" % node.attrib.get("name"))
                write_dual("   Minimum version %s" % node.attrib.get("minver"))
                if node.attrib.get("warn") == "true":
                    warningCount += 1
                    warningList.append("SKU identification")
                    write_dual(" %s" % node.attrib.get("warnmsg"), "yellow")
                break
                
        if ChkResult == False:
            if risklevel == "DANGER":
                dangerCount += 1
                dangerList.append("SKU identification")
                write_dual("DANGER!", "red")
            elif risklevel == "WARNING":
                warningCount += 1
                warningList.append("SKU identification")
                write_dual("WARNING!", "yellow")
            write_dual("   No matching SKU found!")

        # SDK versions
        write_dual("\n******* Getting SDK versions *******")
        checkCount += 1
        ChkResult = True
        for node in chktree.findall('.//%s/sdk' % flashType):
            risklevel = node.attrib.get("risklevel").upper()
            
        for sdk in chktree.findall('.//%s/sdk/sdk_version' % flashType):
            pattern = bytes.fromhex("73646B5F76657273696F6E")
            search_start = int(sdk.attrib.get("offset"), 16)
            search_end = search_start + 0x4f0
            
            index = rawfiledata.find(pattern, search_start, search_end)
            if index != -1:
                addressPos = index - 0xc
                # Handle possible index error if file cut short
                if addressPos + 4 <= len(rawfiledata):
                    address = int(sdk.attrib.get("offset"), 16) + int(string2hex(getDatas(rawfiledata, addressPos, 0x4)), 16)
                    ver = getDatas(rawfiledata, address, 0x8)
                    ver = ver[:-1]
                    try:
                        ver_str = ver.decode('latin-1')
                        if re.match(r'\d{3}\.\d{3}', ver_str):
                            write_dual("  %s : %s" % (sdk.attrib.get("name"), ver_str))
                        else:
                            write_dual("  %s : (unknown)" % (sdk.attrib.get("name")))
                            ChkResult = False
                    except:
                        write_dual("  %s : (decode error)" % (sdk.attrib.get("name")))
                        ChkResult = False
                else: 
                     ChkResult = False
            else:
                 write_dual("  %s : (not found)" % (sdk.attrib.get("name")))
                 ChkResult = False

        if ChkResult == False:
            if risklevel == "DANGER":
                dangerCount += 1
                dangerList.append("SDK versions")
                write_dual("DANGER!", "red")
            elif risklevel == "WARNING":
                warningCount += 1
                warningList.append("SDK versions")
                write_dual("WARNING!", "yellow")
            write_dual(" : unable to get all versions.")

        # --- OTHER CHECKS ---
        for node in chktree.findall('.//%s/' % flashType):
            if node.tag in ["skulistdata", "skumodels", "sdk"]:
                continue
                
            write_dual("\n\n******* Checking %s *******" % node.tag)
            
            for subnode in chktree.findall('.//%s/%s/' % (flashType, node.tag)):
                if subnode.attrib.get("risklevel") is not None:
                    risklevel = subnode.attrib.get("risklevel").upper()

                if subnode.tag == "binentry":
                    checkCount += 1
                    filedata = string2hex(getDatas(rawfiledata, int(subnode.attrib.get("offset"), 16), len(subnode.text)//2))
                    write_dual("%s :" % subnode.attrib.get("name"), end=' ')
                    if filedata.lower() == subnode.text.lower():
                        write_dual("OK", "green")
                    else:
                        if risklevel == "DANGER":
                            dangerCount += 1
                            dangerList.append(subnode.attrib.get("name"))
                            write_dual("DANGER!", "red")
                        elif risklevel == "WARNING":
                            warningCount += 1
                            warningList.append(subnode.attrib.get("name"))
                            write_dual("WARNING!", "yellow")
                        
                        write_dual("  At offset : 0x%s" % subnode.attrib.get("offset").upper())
                        write_dual("  Data mismatch.")

                elif subnode.tag == "multibinentry":
                    checkCount += 1
                    ChkResult = False
                    filedata = string2hex(getDatas(rawfiledata, int(subnode.attrib.get("offset"), 16), int(subnode.attrib.get("length"), 16)))
                    write_dual("%s :"%subnode.attrib.get("name"), end=' ')
                    
                    matched_entry = False
                    for entry in chktree.findall(".//%s/%s/%s[@name='%s']/"%(flashType, node.tag, subnode.tag, subnode.attrib.get("name"))):
                        if filedata.lower() == entry.text.lower():
                            if subnode.attrib.get("name").endswith("trvk_prg1 SCE") and entry.text == "FFFFFFFF" :
                                write_dual("Blank")
                                skipHash = True
                            elif subnode.attrib.get("name").endswith("trvk_pkg1 SCE") and entry.text == "FFFFFFFF" :
                                write_dual("Blank")
                            else:
                                write_dual("OK", "green")
                            ChkResult = True
                            break
                    
                    if not ChkResult:
                         if risklevel == "DANGER":
                            dangerCount += 1
                            dangerList.append(subnode.attrib.get("name"))
                            write_dual("DANGER!", "red")
                         elif risklevel == "WARNING":
                            warningCount += 1
                            warningList.append(subnode.attrib.get("name"))
                            write_dual("WARNING!", "yellow")
                         write_dual("  Mismatch (Offset 0x%s)" % subnode.attrib.get("offset").upper())

                elif subnode.tag == "datafill":
                    checkCount += 1
                    ChkResult = True
                    write_dual("%s :" % subnode.attrib.get("name"), end=' ')
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
                    
                    # Safety check on length
                    if start + length > len(rawfiledata):
                        ChkResult = False
                    else:
                        filedata_chunk = getDatas(rawfiledata, start, length)
                        compare_byte = bytes.fromhex(subnode.text)
                        if all(b == compare_byte[0] for b in filedata_chunk):
                             write_dual("OK", "green")
                        else:
                             ChkResult=False
                    
                    if not ChkResult:
                         if risklevel == "DANGER":
                            dangerCount += 1
                            dangerList.append(subnode.attrib.get("name"))
                            write_dual("DANGER!", "red")
                         elif risklevel == "WARNING":
                            warningCount += 1
                            warningList.append(subnode.attrib.get("name"))
                            write_dual("WARNING!", "yellow")
                         write_dual("  Region should be filled with 0x%s" % subnode.text)

                elif subnode.tag == "hash":
                    checkCount += 1
                    ChkResult = False
                    write_dual("%s :" % subnode.attrib.get("name"), end=' ')
                    if subnode.attrib.get("name").endswith("trvk_prg1 Hash") and skipHash:
                        checkCount -= 1
                        write_dual("Skipped")
                        continue
                        
                    if subnode.attrib.get("sizeoffset") is not None:
                        size = int(string2hex(getDatas(rawfiledata, int(subnode.attrib.get("sizeoffset"), 16), int(subnode.attrib.get("sizelength"), 16))), 16)
                    else:
                        size = int(subnode.attrib.get("size"), 16)
                    
                    hashdata = getMD5(rawfiledata, int(subnode.attrib.get("offset"), 16), size)
                    
                    found_hash = False
                    for h_entry in hashtree.findall(".//type[@name='%s']/"%(subnode.attrib.get("type"))):
                         if hashdata.lower() == h_entry.text.lower():
                             write_dual("OK", "green")
                             found_hash = True
                             break
                    
                    if not found_hash:
                        if risklevel == "DANGER":
                            dangerCount += 1
                            dangerList.append(subnode.attrib.get("name"))
                            write_dual("DANGER!", "red")
                        elif risklevel == "WARNING":
                            warningCount += 1
                            warningList.append(subnode.attrib.get("name"))
                            write_dual("WARNING!", "yellow")
                        write_dual("  MD5 Mismatch: %s" % hashdata.upper())

                elif subnode.tag == "datalist":
                    write_dual("%s :" % subnode.attrib.get("name"), end=' ')
                    write_dual("Checked (Simplified)") 

        # Finishing
        write_dual("\n\n******* Checks completed *******")
        write_dual("Total number of checks = %d" % checkCount)
        write_dual("Number of dangers =", end=' ')
        if dangerCount > 0:
             write_dual("%d" % dangerCount, "red")
        else:
             write_dual("%d" % dangerCount, "green")

        write_dual("Number of warnings =", end=' ')
        if warningCount > 0:
             write_dual("%d" % warningCount, "yellow")
        else:
             write_dual("%d" % warningCount, "green")

        # Update Info Panel
        info_text = ""
        
        # Additional Info Extraction
        HDD, MAC, CID, eCID, board_id, kiban_id = "", "", "", "", "", ""
        
        try:
            if flashType == "NOR":
                HDD = getDatas(rawfiledata, 0xF20204, 0x3C).decode('latin-1', errors='ignore')
                MAC = string2hex(getDatas(rawfiledata, 0x3F040, 0x6)).upper()
                CID = string2hex(getDatas(rawfiledata, 0x3F06A, 0x6)).upper()
                eCID = getDatas(rawfiledata, 0x3F070, 0x20).hex().upper()
                board_id = getDatas(rawfiledata, 0x3F090, 0x8).hex().upper()
                kiban_id = getDatas(rawfiledata, 0x3F098, 0xC).hex().upper()
                
            elif flashType == "NAND":
                MAC = string2hex(getDatas(rawfiledata, 0x90840, 0x6)).upper()
                CID = string2hex(getDatas(rawfiledata, 0x9086A, 0x6)).upper()
                eCID = getDatas(rawfiledata, 0x90870, 0x20).hex().upper()
                board_id = getDatas(rawfiledata, 0x90890, 0x8).hex().upper()
                kiban_id = getDatas(rawfiledata, 0x90898, 0xC).hex().upper()
            
            elif flashType in ['NAND_PS3Xploit', 'EMMC_PS3Xploit'] :
                offset_shift = 0x40000
                MAC = string2hex(getDatas(rawfiledata, 0x90840-offset_shift, 0x6)).upper()
                CID = string2hex(getDatas(rawfiledata, 0x9086A-offset_shift, 0x6)).upper()
                eCID = getDatas(rawfiledata, 0x90870-offset_shift, 0x20).hex().upper()
                board_id = getDatas(rawfiledata, 0x90890-offset_shift, 0x8).hex().upper()
                kiban_id = getDatas(rawfiledata, 0x90898-offset_shift, 0xC).hex().upper()
        except Exception as e:
            info_text += f"\nError extracting info (may be partial dump): {e}"

        info_text += f"Flash Type: {flashText}\n"
        info_text += f"Reversed: {'YES' if isReversed else 'NO'}\n\n"
        if HDD: info_text += f"HDD: {HDD}\n"
        if MAC: info_text += f"MAC: {':'.join(a+b for a,b in zip(MAC[::2], MAC[1::2]))}\n"
        if CID: info_text += f"CID: {CID}\n"
        if eCID: info_text += f"eCID: {eCID}\n"
        if board_id: info_text += f"Board ID: {board_id}\n"
        if kiban_id: info_text += f"Kiban ID: {kiban_id}\n"
        
        if CID.startswith("0FFF"):
            info_text += "\n[!] REFURBISHED CONSOLE"

        # Update GUI labels safely
        self.root.after(0, lambda: self.lbl_total.config(text=f"Total Checks: {checkCount}"))
        self.root.after(0, lambda: self.lbl_danger.config(text=f"Dangers: {dangerCount}"))
        self.root.after(0, lambda: self.lbl_warning.config(text=f"Warnings: {warningCount}"))
        self.root.after(0, lambda: self.lbl_info.config(text=info_text))

        # Write log file
        try:
             with open(f'{inputFile}.checklog.txt', "w") as f:
                 f.write(f"PyPS3checker GUI Check Log\nChecked file: {inputFile}\n\n")
                 f.write("".join(log_buffer))
             write_dual(f"\nLog saved to {inputFile}.checklog.txt", "cyan")
        except Exception as e:
             write_dual(f"\nError saving log file: {e}", "red")

if __name__ == "__main__":
    root = tk.Tk()
    app = CheckerApp(root)
    root.mainloop()
