# PyPS3tools

A suite of Python tools for validating, manipulating, and re-building PS3 flash memory dump files (NOR/NAND/EMMC).

## Disclaimer
> [!WARNING]
> COMPATIBLE WITH PYTHON 3.
> 
> **ALL THESE SOFTWARES ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.**
> USE THEM AT YOUR OWN RISK. The author accepts no responsibility for the consequences of your use of them.

## Installation & Usage

### Linux / macOS

**Requirements:**
- Python 3.x
- Tkinter (usually included, but can be installed via `sudo apt-get install python3-tk`)

**Running the GUI:**
1. Open a terminal in the tool's directory
2. Run the following command:
   ```bash
   python3 checker_gui.py
   ```
   *(Or make it executable with `chmod +x checker_gui.py` and run `./checker_gui.py`)*

**Running CLI Tools:**
Pass the dump file as an argument:
```bash
python3 checker_py3.py dump.bin
```

### Windows

**Method 1: Drag & Drop (Easiest for CLI)**
For the command-line scripts, you can simply **drag and drop your `.bin` dump file onto the corresponding `drag&drop_your_dump_here.bat` file**

**Method 2: Graphical Interface**
To use the new GUI:
1. Ensure Python 3 is installed.
2. Open a terminal in the tool's directory
3. Run the following command:
   ```bash
   python3 checker_gui.py
   ```

## Credits
- Thanks to the entire PS3 dev community.
- Special thanks to LS beta testers.

[![Star History Chart](https://api.star-history.com/svg?repos=littlebalup/PyPS3tools&type=date&legend=top-left)](https://www.star-history.com/#littlebalup/PyPS3tools&type=date&legend=top-left)
