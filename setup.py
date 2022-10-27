import sys
import os
from cx_Freeze import setup, Executable

os.environ['TCL_LIBRARY']="/usr/share/tcltk/tcl8.6"
os.environ['TK_LIBRARY']="/usr/share/tcltk/tk8.6"

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
# build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}
build_exe_options = {"include_files":
                     ["inventory.ico", "images",
                      "LICENSE.txt", "README.md",],
                     "packages":
                     ['sqlalchemy']}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Inventory",
    version="1.0",
    description="A simple inventory software",
    options={"build_exe": build_exe_options},
    executables=[Executable(
        'inventory.py', icon='inventory.ico',
        base=base, copyright='Copyright (c) 2022 Jesus Vedasto Olazo',
        )],
)
