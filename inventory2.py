#!/usr/bin/python

import PySimpleGUI as sg
import os
import sys
from fpdf import FPDF
from datetime import datetime
import time
import webbrowser
import subprocess
from math import ceil

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from dtbase.dtbase import *

__version__ = '2.0'
__author__ = 'Jesus Vedasto Olazo'
__web__ = 'http://jolazo.c1.biz/inventory/'
__email__ = 'jestoy.olazo@gmail.com'
__license__ = 'MIT'

Engine = create_engine('sqlite:///inventory_test_db.db')
if not os.path.isfile('inventory_test_db.db'):
    Base.metadata.create_all(Engine)

Base.metadata.bind = Engine
DBSession = sessionmaker(bind=Engine)

def create_window(theme="Reddit"):
    sg.theme(theme) # sets the theme
    layout = [
        [sg.T('This is an example window.')],
        [sg.B('Close', key='-close_btn-')],
        ]
    window = sg.Window(f'Inventory v{__version__}', layout)
    return window

def main_window():
    window = create_window()
    
    while True:
        event, values = window.read()
        if event in (None, '-close_btn-', sg.WIN_CLOSED):
            break
    
    window.close()

if __name__ == "__main__":
    main_window()