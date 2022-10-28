#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from tkinter.scrolledtext import ScrolledText
from tkinter import simpledialog as sd
import os
from fpdf import FPDF
import sys
from datetime import datetime
import time
import webbrowser
from PIL import Image, ImageTk
import glob
import subprocess
import calendar as cl
from math import ceil
import timeit


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from dtbase.dtbase import *

__version__ = '1.0'
__author__ = 'Jesus Vedasto Olazo'
__web__ = 'http://jolazo.c1.biz/inventory/'
__email__ = 'jestoy.olazo@gmail.com'
__license__ = 'MIT'


Engine = create_engine('sqlite:///inventory_db.db')
if not os.path.isfile('inventory_db.db'):
    Base.metadata.create_all(Engine)

Base.metadata.bind = Engine
DBSession = sessionmaker(bind=Engine)

def image_list(size=(16, 16)):
    """This creates a dictionary of image file path for software icons."""
    img_lst = {}
    for img in glob.glob('images/*.png'):
        path_to_file = img
        img = os.path.basename(img)
        file_name = img.split('.')[0]
        img_lst[file_name] = ImageTk.PhotoImage(Image.open(path_to_file).resize(size))
    return img_lst

class MainWindow(ttk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super(MainWindow, self).__init__(master, *args, **kwargs)
        self.master.geometry('900x600+10+10')
        self.master.title('Inventory Management '+__version__)
        self.master.protocol('WM_DELETE_WINDOW', self.close_app)
        self.style = ttk.Style()
        self.img36_list = image_list(size=(36, 36))
        self.img16_list = image_list()
        if os.name == "nt":
            self.master.state("zoomed")
            self.master.iconbitmap("inventory.ico")
        elif os.name == "posix":
            self.master.attributes("-zoomed", True)
            self.master.tk.call('wm', 'iconphoto', self.master._w,
                                self.img36_list['inventory'])
        self.setup_ui()

    def setup_ui(self):
        # Start of styling
        self.style.configure('Treeview.Heading', font='Times 11 italic')
        # End of styling
        # Start of menubar
        menubar = tk.Menu(self)
        self.master.config(menu=menubar)

        filemenu = tk.Menu(menubar, tearoff=0)
        optionmenu = tk.Menu(menubar, tearoff=0)
        themesmenu = tk.Menu(optionmenu, tearoff=0)
        reportmenu = tk.Menu(optionmenu, tearoff=0)
        helpmenu = tk.Menu(menubar, tearoff=0)

        menubar.add_cascade(label='File', menu=filemenu, underline=0)
        menubar.add_cascade(label='Option', menu=optionmenu, underline=0)
        menubar.add_cascade(label='Report', menu=reportmenu, underline=0)
        menubar.add_cascade(label='Help', menu=helpmenu, underline=0)

        optionmenu.add_cascade(label='Themes', menu=themesmenu)
        self.radio_var = tk.IntVar()
        self.radio_var.set(self.style.theme_names().index(self.style.theme_use())+1)
        for idx, theme in enumerate(self.style.theme_names()):
            themesmenu.add_radiobutton(label=theme, value=idx+1, variable=self.radio_var, command=self.change_theme)

        filemenu.add_command(label='Incoming', underline=0, accelerator='Ctrl+Shift+I', image=self.img16_list['incoming'], command=self.incoming_window, compound=tk.LEFT)
        filemenu.add_command(label='Outgoing', image=self.img16_list['outgoing'], command=self.outgoing_window, compound=tk.LEFT)
        filemenu.add_separator()
        filemenu.add_command(label='Unit Master', image=self.img16_list['measure'], command=self.unit_window, compound=tk.LEFT)
        filemenu.add_command(label='Bin Master', image=self.img16_list['location'], command=self.bin_window, compound=tk.LEFT)
        filemenu.add_command(label='Product Master', image=self.img16_list['material'], command=self.product_window, compound=tk.LEFT)
        filemenu.add_command(label='Supplier Master', image=self.img16_list['supplier'], command=self.supplier_window, compound=tk.LEFT)
        filemenu.add_command(label='Project Master', image=self.img16_list['project1'], command=self.project_window, compound=tk.LEFT)
        filemenu.add_separator()
        filemenu.add_command(label='Quit', accelerator='Ctrl+Q', underline=0, image=self.img16_list['quit'], command=self.close_app, compound=tk.LEFT)
        helpmenu.add_command(label='Help', image=self.img16_list['help'], compound=tk.LEFT)
        helpmenu.add_separator()
        helpmenu.add_command(label='About', image=self.img16_list['about'], compound=tk.LEFT, command=self.about_window)
        reportmenu.add_command(label='Current Stock', image=self.img16_list['material'], compound=tk.LEFT, command=self.show_current_stock)
        reportmenu.add_command(label="Sticker", image=self.img16_list['material'], compound=tk.LEFT, command=self.show_sticker)
        # End of menubar

        # Start of Toolbox
        graph_frame = ttk.Frame(self)
        graph_frame.pack(fill=tk.X, padx=5, pady=5)
        self.tool_box = ttk.Frame(self)
        self.tool_box.pack(fill=tk.X, padx=5, pady=5)

        self.unit_btn = ttk.Button(self.tool_box, image=self.img36_list['measure'])
        self.unit_btn.pack(side=tk.LEFT)
        CreateToolTip(self.unit_btn, 'Unit Master')
        self.unit_btn.config(command=self.unit_window)

        self.loca_btn = ttk.Button(self.tool_box, image=self.img36_list['location'])
        self.loca_btn.pack(side=tk.LEFT)
        CreateToolTip(self.loca_btn, 'Bin Master')
        self.loca_btn.config(command=self.bin_window)

        self.prod_btn = ttk.Button(self.tool_box, image=self.img36_list['material'])
        self.prod_btn.pack(side=tk.LEFT)
        CreateToolTip(self.prod_btn, 'Product Master')
        self.prod_btn.config(command=self.product_window)

        self.supp_btn = ttk.Button(self.tool_box, image=self.img36_list['supplier'])
        self.supp_btn.pack(side=tk.LEFT)
        CreateToolTip(self.supp_btn, 'Supplier Master')
        self.supp_btn.config(command=self.supplier_window)

        self.proj_btn = ttk.Button(self.tool_box, image=self.img36_list['project1'])
        self.proj_btn.pack(side=tk.LEFT)
        CreateToolTip(self.proj_btn, 'Project Master')
        self.proj_btn.config(command=self.project_window)

        self.incg_btn = ttk.Button(self.tool_box, image=self.img36_list['incoming'])
        self.incg_btn.pack(side=tk.LEFT)
        CreateToolTip(self.incg_btn, 'Incoming')
        self.incg_btn.config(command=self.incoming_window)

        self.outg_btn = ttk.Button(self.tool_box, image=self.img36_list['outgoing'])
        self.outg_btn.pack(side=tk.LEFT)
        CreateToolTip(self.outg_btn, 'Outgoing')
        self.outg_btn.config(command=self.outgoing_window)

        self.search_entry = ttk.Entry(self.tool_box, width=50)
        self.search_entry.pack(side=tk.RIGHT)
        #self.search_entry.bind('<KeyPress-Return>', self.search_event)
        self.search_btn = ttk.Button(self.tool_box, text='Search', image=self.img16_list['search'], compound=tk.LEFT)
        self.search_btn.pack(side=tk.RIGHT)
        self.search_btn.config(command=self.search_record)

        self.details_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.details_pane.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.left_frame = ttk.Frame(self.details_pane)
        self.right_frame = ttk.Frame(self.details_pane)

        self.details_pane.add(self.left_frame, weight=3)
        self.details_pane.add(self.right_frame, weight=1)

        self.prod_view = ttk.Treeview(self.left_frame)
        self.prod_view.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        prod_cols = ('item_code', 'item_name', 'unit', 'price', 'quantity', 'amount')
        self.prod_view['columns'] = prod_cols

        self.prod_view.column('#0', width=50, stretch=False)
        self.prod_view.heading('#0', text='Id')

        self.prod_view.bind('<<TreeviewSelect>>', self.load_location)

        for prod_col in prod_cols:
            self.prod_view.heading(prod_col, text=prod_col.replace('_', ' ').title())
            if prod_col == 'price':
                self.prod_view.column(prod_col, width=50, stretch=False, anchor='e')
            if prod_col == 'unit':
                self.prod_view.column(prod_col, width=50, stretch=False, anchor='center')
            if prod_col == 'quantity':
                self.prod_view.column(prod_col, width=75, stretch=False, anchor='center')
            if prod_col == 'item_code':
                self.prod_view.column(prod_col, width=100, stretch=False)
            if prod_col == 'item_name':
                self.prod_view.column(prod_col, width=200, stretch=False)
            if prod_col == 'amount':
                self.prod_view.column(prod_col, anchor='center')

        self.prod_view.tag_configure("odd", background="#d5f4e6")
        self.prod_view.tag_configure("even", background="#80ced6")

        self.vbar1 = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL)
        self.vbar1.pack(side=tk.RIGHT, fill=tk.Y)

        self.vbar1.config(command=self.prod_view.yview)
        self.prod_view['yscrollcommand'] = self.vbar1.set

        self.loca_view = ttk.Treeview(self.right_frame)
        self.loca_view.pack(expand=True, fill=tk.BOTH)
        loca_cols = ('location', 'stock')
        self.loca_view['columns'] = loca_cols

        self.loca_view.column('#0', width=50, stretch=False)
        self.loca_view.heading('#0', text='Id')

        for loca_col in loca_cols:
            self.loca_view.heading(loca_col, text=loca_col.title())
            if loca_col != 'location':
                self.loca_view.column(loca_col, width=150, stretch=False, anchor='center')
            else:
                self.loca_view.column(loca_col, anchor='center')

        self.loca_view.tag_configure("odd", background="#d5f4e6")
        self.loca_view.tag_configure("even", background="#80ced6")
        
        self.print_btn = ttk.Button(self.right_frame, text='Print')
        self.print_btn.pack(side=tk.LEFT, padx=3, pady=3)
        self.print_btn.config(command=self.print_location)

        sum_frame = ttk.LabelFrame(graph_frame, text='Summary:')
        sum_frame.pack(side=tk.LEFT, padx=5, pady=5)

        self.demo1 = Demo(sum_frame)
        self.demo1.pack(side=tk.LEFT)

        self.demo2 = Demo(sum_frame)
        self.demo2.pack(side=tk.LEFT)

        self.demo3 = Demo(sum_frame)
        self.demo3.pack(side=tk.LEFT)

        self.title_lbl = tk.Label(graph_frame, text='Inventory\nManagement 1.0', foreground='#6B266B', font='Times 36 bold italic')
        self.title_lbl.pack(side=tk.RIGHT, padx=5, pady=5)

        close_btn = ttk.Button(self, text='Close', image=self.img16_list['cancel'], compound=tk.LEFT)
        close_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        close_btn.config(command=self.close_app)
        
    def print_location(self):
        line = self.prod_view.focus()
        if line == '':
            return
        item = self.prod_view.item(line)['values']
        children = self.loca_view.get_children()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Times', '', 12)
        pdf.cell(100, 10, f'{item[0]} {item[1]} {item[2]} {item[4]}', 0, 1, 'L')
        if len(children) != 0:
            for idx in children:
                values = self.loca_view.item(idx)['values']
                pdf.cell(15, 10, f"{str(values[0])} --> {str(values[1])}", 0, 1, 'L')
        pdf.output('location.pdf', 'F')
        if os.name == 'nt':
            CREATE_NO_WINDOW = 0x08000000
            subprocess.call(["start", 'location.pdf'], creationflags=CREATE_NO_WINDOW, shell=True)
        else:
            os.system("xdg-open %s"% ('location.pdf',))
        

    def show_sticker(self):
        loc_name = sd.askstring("Location", "Please enter location:", parent=self)
        if loc_name == None:
            return
        session = DBSession()
        loc_record = session.query(BinLocation).filter(BinLocation.code == loc_name).first()
        if loc_record == None:
            mb.showerror("Report Error", "Location not available in the database")
            session.close()
            return
        in_records = session.query(Incoming).join(BinLocation).filter(BinLocation.id == loc_record.id).all()
        if len(in_records) == 0:
            session.close()
            return
        out_records = session.query(Outgoing).join(BinLocation).filter(BinLocation.id == loc_record.id).all()
        pro_dict = {}
        for record in in_records:
            if record.products.code in pro_dict.keys():
                pro_dict[record.products.code][2] = pro_dict[record.products.code][2] + record.quantity
            else:
                pro_dict[record.products.code] = [record.name, record.products.units.code, record.quantity, 0]
        if len(out_records) != 0:
            for record in out_records:
                if record.products.code in pro_dict.keys():
                    pro_dict[record.products.code][3] = pro_dict[record.products.code][3] + record.quantity
                else:
                    pro_dict[record.products.code] = [record.name, record.products.units.code, 0, record.quantity]

        pdf = FPDF()
        pdf.add_page()
        for k, v in pro_dict.items():
            if (v[2]+v[3]) != 0:
                print(k, v[0], v[1], v[2]+v[3])
                pdf.set_font('Times', 'B', 40)
                pdf.cell(145, 10, k,0,0,'L')
                if type(v[2]+v[3]) == float:
                    tot_str = str(v[2]+v[3]).split(".")
                    if int(tot_str[1]) == 0:
                        pdf.cell(35, 10, f"{tot_str[0]} {v[1]}",0,1,"C")
                    else:
                        pdf.cell(35, 10, f"{'.'.join(tot_str)} {v[1]}",0,1,"C")
                else:
                    pdf.cell(35, 10, f"{v[2]+v[3]} {v[1]}",0,1,"C")
                pdf.ln(5)
                pdf.set_font('Times', '', 30)
                pdf.cell(190,10,v[0][0:25],0,1,'L')
                pdf.ln(10)
        pdf.set_font('Times', 'B', 50)
        pdf.set_y(-50)
        pdf.cell(190, 10, loc_record.code, 0, 0, "C")
        pdf.output('output.pdf', 'F')
        if os.name == 'nt':
            CREATE_NO_WINDOW = 0x08000000
            subprocess.call(["start", 'output.pdf'], creationflags=CREATE_NO_WINDOW, shell=True)
        else:
            os.system("xdg-open %s"% ('output.pdf',))
        session.close()

    def show_current_stock(self):
        filename = fd.asksaveasfilename(parent=self, defaultextension='.pdf', initialfile="CurrentStock")
        product = self.incg_dict()
        if filename == '':
            return
        pdf = PDF('L')
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_fill_color(255, 255, 255)
        total = 0
        counter = 1
        for key, value in product.items():
            sub_total = value['quantity'] * value['price']
            if sub_total != 0:
                pdf.cell(20, 8, f'{counter}', 1, 0, 'C', True)
                pdf.cell(35, 8, f'{key}', 1, 0, 'C', True)
                pdf.cell(100, 8, f"{value['description']}", 1, 0, 'C', True)
                pdf.cell(30, 8, f"{value['unit']}", 1, 0, 'C', True)
                pdf.cell(30, 8, f"{value['price']:,.2f}", 1, 0, 'C', True)
                pdf.cell(30, 8, f"{value['quantity']:,.2f}", 1, 0, 'C', True)
                total += sub_total
                pdf.cell(0, 8, f"{sub_total:,.2f}", 1, 1, 'C', True)
                counter += 1
        pdf.set_font('Times', 'BI', 12)
        pdf.cell(20, 8, "", 1, 0, 'C', True)
        pdf.cell(35, 8, "", 1, 0, 'C', True)
        pdf.cell(100, 8, "", 1, 0, 'C', True)
        pdf.cell(30, 8, "", 1, 0, 'C', True)
        pdf.cell(30, 8, "", 1, 0, 'C', True)
        pdf.cell(30, 8, "Total", 1, 0, 'C', True)
        pdf.cell(0, 8, f"{total:,.2f}", 1, 0, 'C', True)

        pdf.output(filename, 'F')
        if os.name == 'nt':
            CREATE_NO_WINDOW = 0x08000000
            subprocess.call(["start", filename], creationflags=CREATE_NO_WINDOW, shell=True)
        else:
            os.system("xdg-open %s"% (filename,))

    def about_window(self):
        tp = tk.Toplevel(self)
        win = AboutWindow(tp)
        win.pack(expand=True, fill=tk.BOTH, padx=2, pady=2)

    def draw_graph(self):
        demo_format1 = self.calculate('inventory')
        self.demo1.draw(270, demo_format1[1], demo_format1[0], 'Inventory', color='#FF0000')

        demo_format2 = self.calculate()
        self.demo2.draw(270, demo_format2[1], demo_format2[0], 'Received', color='#800080')

        demo_format3 = self.calculate('outgoing')
        self.demo3.draw(270, demo_format3[1], demo_format3[0], 'Issued', color='#008000')

    def calculate(self, detail='incoming'):
        session = DBSession()
        total = 0
        in_total = 0
        out_total = 0
        pos = 0
        percentage = 0
        in_records = session.query(Incoming).options(joinedload(Incoming.products)).all()
        out_records = session.query(Outgoing).options(joinedload(Outgoing.products)).all()
        for in_record in in_records:
            in_total+=(in_record.quantity * in_record.products.price)
        for out_record in out_records:
            out_total+=(abs(out_record.quantity) * out_record.products.price)
        session.close()
        if detail == 'inventory':
            total = in_total - out_total
            try:
                percentage = 1 - (total/in_total)
                pos = 359 - ceil(359*percentage)
            except:
                pos = 1
        elif detail == 'outgoing':
            total = out_total
            if total != 0:
                percentage = total/in_total
                pos = ceil(359*percentage)
            else:
                pos = 1
        else:
            total = in_total
            if total > 0:
                pos = 359
            else:
                pos = 1
        return (total, pos)

    def update_view(self):
        children = self.prod_view.get_children()
        self.prod_view.delete(*children)
        product = self.incg_dict()
        counter = 1
        for key,value in product.items():
            values = (key, value['description'], value['unit'],
                    f'{value["price"]:,.2f}', value['quantity'],
                    f'{value["quantity"]*value["price"]:,.2f}')
            if value['quantity'] != 0:
                if counter % 2 == 0:
                    self.prod_view.insert('', tk.END, str(counter), text=str(counter), values=values, tags='even')
                else:
                    self.prod_view.insert('', tk.END, str(counter), text=str(counter), values=values, tags='odd')
                counter += 1
        self.draw_graph()

    def incg_dict(self):
        session = DBSession()
        records = session.query(Incoming).options(joinedload(Incoming.products)).all()
        out_recs = session.query(Outgoing).options(joinedload(Outgoing.products)).all()
        product = {}
        for record in records:
            if record.products.code in product.keys():
                product[record.products.code]['quantity'] += record.quantity
            else:
                data = {'description': record.products.name, 'unit': record.products.units.code,
                        'quantity': record.quantity, 'price': record.products.price}
                product[record.products.code] = data
        for out_rec in out_recs:
            if out_rec.products.code in product.keys():
                product[out_rec.products.code]['quantity'] += out_rec.quantity
        session.close()
        return product

    def unit_window(self):
        tp = tk.Toplevel(self)
        win = UnitWindow(tp)
        win.pack(expand=True, fill=tk.BOTH)
        self.wait_window(tp)

    def bin_window(self):
        tp = tk.Toplevel(self)
        win = BinWindow(tp)
        win.pack(expand=True, fill=tk.BOTH)
        self.wait_window(tp)

    def product_window(self):
        tp = tk.Toplevel(self)
        win = ProductWindow(tp)
        win.pack(expand=True, fill=tk.BOTH)
        self.wait_window(tp)

    def project_window(self):
        tp = tk.Toplevel(self)
        win = ProjectWindow(tp)
        win.pack(expand=True, fill=tk.BOTH)
        self.wait_window(tp)

    def supplier_window(self):
        tp = tk.Toplevel(self)
        win = SupplierWindow(tp)
        win.pack(expand=True, fill=tk.BOTH)
        self.wait_window(tp)

    def incoming_window(self):
        tp = tk.Toplevel(self)
        win = IncomingWindow(tp)
        win.pack(expand=True, fill=tk.BOTH)
        self.wait_window(tp)
        self.update_view()

    def outgoing_window(self):
        tp = tk.Toplevel(self)
        win = OutgoingWindow(tp)
        win.pack(expand=True, fill=tk.BOTH)
        self.wait_window(tp)
        self.update_view()

    def search_event(self, event):
        self.search_record()

    def search_record(self):
        item = self.search_entry.get()
        if item == '':
            mb.showwarning('Invalid Keyword', f'Invalid keyword "{item}", please try again')
            self.search_entry.focus_set()
            return
        elif item.lower() == 'all' :
            self.update_view()
            self.search_entry.focus_set()
            return
        session = DBSession()
        records = session.query(Incoming).join(Products).filter(Products.name.like(f'%{item}%')).all()
        product = {}
        if len(records) == 0:
            session.close()
            mb.showwarning('No Records', 'No records to show.')
            self.search_entry.focus_set()
            return

        for record in records:
            if record.products.code in product.keys():
                product[record.products.code]['quantity'] += record.quantity
            else:
                data = {'description': record.products.name, 'unit': record.products.units.code,
                        'quantity': record.quantity, 'price': record.products.price}
                product[record.products.code] = data
        out_recs = session.query(Outgoing).join(Products).all()
        for out_rec in out_recs:
            if out_rec.products.code in product.keys():
                product[out_rec.products.code]['quantity'] += out_rec.quantity
        session.close()

        # insert to prod_view
        children = self.prod_view.get_children()
        self.prod_view.delete(*children)
        counter = 1
        for key,value in product.items():
            values = (key, value['description'], value['unit'],
                    f'{value["price"]:,.2f}', value['quantity'],
                    f'{value["quantity"]*value["price"]:,.2f}')
            if value['quantity'] != 0:
                if counter % 2 == 0:
                    self.prod_view.insert('', tk.END, str(counter), text=str(counter), values=values, tags='even')
                else:
                    self.prod_view.insert('', tk.END, str(counter), text=str(counter), values=values, tags='odd')
                counter += 1
        self.search_entry.delete('0', tk.END)
        self.search_entry.focus_set()

    def load_location(self, event):
        print(event.type) # Some bug is here.
        item = self.prod_view.focus()
        if item == '':
            mb.showwarning('No record', 'No record')
        else:
            if type(self.prod_view.item(item)['values'][0]) == int:
                item = "%s" % ("{:010}".format(self.prod_view.item(item)['values'][0]),)
            else:
                item = self.prod_view.item(item)['values'][0]
        children = self.loca_view.get_children()
        self.loca_view.delete(*children)
        location = {}
        session = DBSession()
        records = session.query(Incoming).join(Products, BinLocation).filter(Products.code == item).all()
        for record in records:
            if record.binlocation.code in location.keys():
                location[record.binlocation.code] += record.quantity
            else:
                location[record.binlocation.code] = record.quantity
        out_recs = session.query(Outgoing).join(Products, BinLocation).filter(Products.code == item).all()
        for out_rec in out_recs:
            if out_rec.binlocation.code in location.keys():
                location[out_rec.binlocation.code] += out_rec.quantity
        counter = 1
        for key, value in location.items():
            values = (key, f'{value:,.2f}')
            if value != 0:
                if counter % 2 == 0:
                    self.loca_view.insert('', tk.END, str(counter), text=str(counter), tags='even', values=values)
                else:
                    self.loca_view.insert('', tk.END, str(counter), text=str(counter), tags='odd', values=values)
                counter += 1
        session.close()

    def change_theme(self):
        idx = self.radio_var.get() - 1
        self.style.theme_use(self.style.theme_names()[idx])

    def close_app(self):
        self.master.destroy()

class CreateToolTip(object):

    def __init__(self, widget, message):
        self.message = message
        widget.bind("<Enter>", self.tooltip_show)
        widget.bind("<Leave>", self.tooltip_close)

    def tooltip_show(self, event):
        """ This function is used to display the tool tip. """
        x_coor = event.widget.winfo_rootx()+20
        y_coor = event.widget.winfo_rooty()+30

        time.sleep(0.2)
        self.tool_tip_win = tk.Toplevel(event.widget)
        self.tool_tip_win.overrideredirect(True)
        loc = "+" + str(x_coor) + "+" + str(y_coor)
        self.tool_tip_win.geometry(loc)
        msg = tk.Label(self.tool_tip_win, text=self.message,
                       fg='white', bg='#2596be')
        msg.pack(fill=tk.X, ipadx=5, ipady=5)
        msg.config(font="Helvetica 8 bold")

    def tooltip_close(self, event):
        """ This enables the tooltip to destroy itself when leave the widget """
        self.tool_tip_win.destroy()

class Demo(tk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super(Demo, self).__init__(master, *args, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        self.cv = tk.Canvas(self, height=150, width=150)
        self.cv.pack(padx=10, pady=10)
        # self.btn = ttk.Button(self, text='Update')
        # self.btn.config(command=lambda: self.draw(45, 135, 65))
        # self.btn.pack(padx=10, pady=10)

    def draw(self, start, extent, amount, descp, color='#FF9797'):
        self.cv.delete('all')
        self.cv.create_oval(5,5,145,145, fill="white", outline='white', width=1.5)
        self.cv.create_oval(5,5,145,145, fill="white", outline='white', width=1)
        self.cv.create_arc(5,5,145,145,fill=color,start=start,
                         extent=extent, outline=color, width=1.5)
        self.cv.create_arc(5,5,145,145,fill=color,start=start,
                         extent=extent, outline=color, width=1)
        self.cv.create_oval(15,15,135,135,fill='#DAD615', outline="#DAD615", width=1.5)
        self.cv.create_oval(15,15,135,135,fill='#DAD615', outline="#DAD615", width=1)

        self.cv.create_text(75,68, text=f'{amount:,.2f}', font=('helvetica', 12, 'bold'))
        self.cv.create_text(75,84, text=f'{descp}', font=('helvetica', 10, 'bold'))
        self.cv.update()

# Start of UnitWindow class
class UnitWindow(ttk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super(UnitWindow, self).__init__(master, *args, **kwargs)
        self.master.protocol('WM_DELETE_WINDOW', self.close_app)
        self.master.title('Units')
        self.master.geometry('500x400')
        self.img16_list = image_list()
        self.style = ttk.Style()
        self.record_id = None
        if os.name == "nt":
            self.master.iconbitmap('inventory.ico')
        self.setup_ui()

    def setup_ui(self):
        self.style.configure('Custom.TLabel', font='Times 24 italic', foreground='#911818')
        title_lbl = ttk.Label(self, text='Units', style='Custom.TLabel')
        title_lbl.pack(fill=tk.X, padx=5, pady=5)

        top_frame = ttk.Frame(self)
        top_frame.pack(expand=True, fill=tk.BOTH)
        bot_frame = ttk.Frame(self)
        bot_frame.pack(fill=tk.X)

        self.tr_lblframe = ttk.LabelFrame(top_frame, text='Transaction')
        self.tr_lblframe.pack(
                            side=tk.LEFT, ipadx=10, ipady=10,
                            expand=True, fill=tk.BOTH, padx=5, pady=5)

        unit_lbl = ttk.Label(self.tr_lblframe, text='Unit Code:')
        unit_lbl.pack(anchor=tk.W, padx=5, pady=5)
        self.code_entry = ttk.Entry(self.tr_lblframe)
        self.code_entry.pack(fill=tk.X, padx=5, pady=5)

        name_lbl = ttk.Label(self.tr_lblframe, text='Unit Name:')
        name_lbl.pack(anchor=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.tr_lblframe)
        self.name_entry.pack(fill=tk.X, padx=5, pady=5)

        self.save_btn = ttk.Button(self.tr_lblframe, text='Save', image=self.img16_list['save'], compound=tk.LEFT)
        self.save_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.save_btn.config(command=self.save_record)

        self.edit_btn = ttk.Button(self.tr_lblframe, text='Edit', image=self.img16_list['edit'], compound=tk.LEFT)
        self.edit_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.edit_btn.config(command=self.edit_record)

        self.del_btn = ttk.Button(self.tr_lblframe, text='Delete', image=self.img16_list['minus'], compound=tk.LEFT)
        self.del_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.del_btn.config(command=self.delete_record)

        self.unit_view = ttk.Treeview(top_frame)
        self.unit_view.pack(
                            expand=True, fill=tk.BOTH,
                            side=tk.LEFT, padx=5, pady=5)
        self.unit_view['columns'] = ('code', 'name')
        self.unit_view.heading('#0', text='Id')
        self.unit_view.heading('code', text='Code')
        self.unit_view.heading('name', text='Name')
        self.unit_view.column('#0', width=50, stretch=False)
        self.unit_view.column('code', width=50, stretch=False)

        self.vbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.LEFT, fill=tk.Y)

        self.vbar.config(command=self.unit_view.yview)
        self.unit_view['yscrollcommand'] = self.vbar.set

        self.unit_view.tag_configure("odd", background="#d5f4e6", font=('Times', 11, 'bold'))
        self.unit_view.tag_configure("even", background="#80ced6", font=('Times', 11, 'bold'))

        self.close_btn = ttk.Button(bot_frame, text='Close', image=self.img16_list['cancel'], compound=tk.LEFT)
        self.close_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.close_btn.config(command=self.close_app)
        self.update_view()
        self.code_entry.focus_set()

    def update_view(self):
        session = DBSession()
        records = session.query(Units).all()
        if len(records) == 0:
            print('Sorry no records has been found.')
            session.close()
            return

        children = self.unit_view.get_children()
        if len(children) != 0:
            for child in children:
                self.unit_view.delete(child)
        counter = 1
        for record in records:
            if counter % 2 == 0:
                self.unit_view.insert('', tk.END, str(record.id), text=str(record.id), tags='odd')
            else:
                self.unit_view.insert('', tk.END, str(record.id), text=str(record.id), tags='even')
            self.unit_view.set(str(record.id), 'code', record.code)
            self.unit_view.set(str(record.id), 'name', record.name)
            counter+=1
        session.close()

    def save_record(self):
        code = self.code_entry.get()
        name = self.name_entry.get()
        if (code == '') or (name == ''):
            mb.showwarning('Incomplete Data', 'Sorry missing data, \n record cannot be save.')
            self.code_entry.focus_set()
            return
        session = DBSession()
        if self.record_id == None:
            new_record = Units(code=code, name=name)
            session.add(new_record)
        else:
            record = session.query(Units).filter(Units.id == self.record_id).first()
            record.code = code
            record.name = name
            self.record_id = None
        session.commit()
        session.close()
        self.code_entry.delete('0', tk.END)
        self.name_entry.delete('0', tk.END)
        self.update_view()
        self.code_entry.focus_set()

    def edit_record(self):
        select_unit = self.unit_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        self.record_id = record_id
        session = DBSession()
        record = session.query(Units).filter(Units.id == record_id).first()
        self.code_entry.delete('0', tk.END)
        self.name_entry.delete('0', tk.END)
        code = record.code
        name = record.name
        self.code_entry.insert(tk.END, code)
        self.name_entry.insert(tk.END, name)
        session.close()
        self.code_entry.focus_set()

    def delete_record(self):
        select_unit = self.unit_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        session = DBSession()
        record = session.query(Units).filter(Units.id == record_id).first()
        answer = mb.askyesno('Delete?', 'Are you sure you want to delete?')
        if answer:
            session.delete(record)
            session.commit()
        session.close()
        self.update_view()
        self.code_entry.focus_set()

    def close_app(self):
        self.master.destroy()
# End of UnitWindow class

# Start of BinWindow class
class BinWindow(ttk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super(BinWindow, self).__init__(master, *args, **kwargs)
        self.master.protocol('WM_DELETE_WINDOW', self.close_app)
        self.master.title('Location Bin')
        #self.master.geometry('500x400')
        self.img16_list = image_list()
        self.style = ttk.Style()
        self.record_id = None
        if os.name == "nt":
            self.master.iconbitmap('inventory.ico')
        self.setup_ui()

    def setup_ui(self):
        self.style.configure('Custom.TLabel', font='Times 24 italic', foreground='#911818')
        title_lbl = ttk.Label(self, text='Location Bin', style='Custom.TLabel')
        title_lbl.pack(fill=tk.X, padx=5, pady=5)

        top_frame = ttk.Frame(self)
        top_frame.pack(expand=True, fill=tk.BOTH)
        bot_frame = ttk.Frame(self)
        bot_frame.pack(fill=tk.X)

        self.tr_lblframe = ttk.LabelFrame(top_frame, text='Transaction')
        self.tr_lblframe.pack(
                            side=tk.LEFT, ipadx=10, ipady=10,
                            expand=True, fill=tk.BOTH, padx=5, pady=5)

        unit_lbl = ttk.Label(self.tr_lblframe, text='Location Code:')
        unit_lbl.pack(anchor=tk.W, padx=5, pady=5)
        self.code_entry = ttk.Entry(self.tr_lblframe)
        self.code_entry.pack(fill=tk.X, padx=5, pady=5)

        self.save_btn = ttk.Button(self.tr_lblframe, text='Save', image=self.img16_list['save'], compound=tk.LEFT)
        self.save_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.save_btn.config(command=self.save_record)

        self.edit_btn = ttk.Button(self.tr_lblframe, text='Edit', image=self.img16_list['edit'], compound=tk.LEFT)
        self.edit_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.edit_btn.config(command=self.edit_record)

        self.del_btn = ttk.Button(self.tr_lblframe, text='Delete', image=self.img16_list['minus'], compound=tk.LEFT)
        self.del_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.del_btn.config(command=self.delete_record)

        self.location_view = ttk.Treeview(top_frame)
        self.location_view.pack(
                            expand=True, fill=tk.BOTH,
                            side=tk.LEFT, padx=5, pady=5)
        self.location_view['columns'] = ('code',)
        self.location_view.heading('#0', text='Id')
        self.location_view.heading('code', text='Code')
        self.location_view.column('#0', width=60, stretch=False)

        self.vbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.LEFT, fill=tk.Y)

        self.vbar.config(command=self.location_view.yview)
        self.location_view['yscrollcommand'] = self.vbar.set

        self.location_view.tag_configure("odd", background="#d5f4e6")
        self.location_view.tag_configure("even", background="#80ced6")

        self.close_btn = ttk.Button(bot_frame, text='Close', image=self.img16_list['cancel'], compound=tk.LEFT)
        self.close_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.close_btn.config(command=self.close_app)
        self.update_view()
        self.code_entry.focus_set()

    def update_view(self):
        session = DBSession()
        records = session.query(BinLocation).all()
        if len(records) == 0:
            print('Sorry no records has been found.')
            session.close()
            return

        children = self.location_view.get_children()
        self.location_view.delete(*children)
        counter = 1
        for record in records:
            if counter % 2 == 0:
                self.location_view.insert('', tk.END, str(record.id), text=str(record.id), tags='odd', values=(record.code,))
            else:
                self.location_view.insert('', tk.END, str(record.id), text=str(record.id), tags='even', values=(record.code,))
            counter+=1
        session.close()

    def save_record(self):
        code = self.code_entry.get()
        if code == '':
            mb.showwarning('Incomplete Data', 'Sorry missing data, \n record cannot be save.')
            self.code_entry.focus_set()
            return
        session = DBSession()
        if self.record_id == None:
            new_record = BinLocation(code=code)
            session.add(new_record)
        else:
            record = session.query(BinLocation).filter(BinLocation.id == self.record_id).first()
            record.code = code
            self.record_id = None
        session.commit()
        session.close()
        self.code_entry.delete('0', tk.END)
        self.update_view()
        self.code_entry.focus_set()

    def edit_record(self):
        select_unit = self.location_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        self.record_id = record_id
        session = DBSession()
        record = session.query(BinLocation).filter(BinLocation.id == record_id).first()
        self.code_entry.delete('0', tk.END)
        code = record.code
        self.code_entry.insert(tk.END, code)
        session.close()
        self.code_entry.focus_set()

    def delete_record(self):
        select_unit = self.location_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        session = DBSession()
        record = session.query(BinLocation).filter(BinLocation.id == record_id).first()
        answer = mb.askyesno('Delete?', 'Are you sure you want to delete?')
        if answer:
            session.delete(record)
            session.commit()
        session.close()
        self.update_view()
        self.code_entry.focus_set()

    def close_app(self):
        self.master.destroy()
# End of BinWindow class

# Start of ProductWindow class
class ProductWindow(ttk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super(ProductWindow, self).__init__(master, *args, **kwargs)
        self.master.protocol('WM_DELETE_WINDOW', self.close_app)
        self.master.title('Products')
        self.master.geometry('800x600+20+20')
        self.img16_list = image_list()
        self.style = ttk.Style()
        self.record_id = None
        if os.name == "nt":
            self.master.iconbitmap('inventory.ico')
        self.setup_ui()

    def setup_ui(self):
        self.style.configure('Custom.TLabel', font='Times 24 italic', foreground='#911818')

        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(title_frame, text='Products', style='Custom.TLabel')
        title_lbl.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)

        self.search_entry = ttk.Entry(title_frame)
        self.search_entry.pack(side=tk.RIGHT, padx=5, pady=5)
        self.search_entry.config(width=40)
        self.search_entry.bind('<KeyPress-Return>', self.search_event)

        self.search_btn = ttk.Button(title_frame, text='Search', image=self.img16_list['search'], compound=tk.LEFT)
        self.search_btn.pack(side=tk.RIGHT)
        self.search_btn.config(command=self.search_record)

        top_frame = ttk.Frame(self)
        top_frame.pack(expand=True, fill=tk.BOTH)
        bot_frame = ttk.Frame(self)
        bot_frame.pack(fill=tk.X)

        self.tr_lblframe = ttk.LabelFrame(top_frame, text='Transaction')
        self.tr_lblframe.pack(
                            side=tk.LEFT, ipadx=10, ipady=10,
                            expand=True, fill=tk.BOTH, padx=5, pady=5)

        code_lbl = ttk.Label(self.tr_lblframe, text='Item Code:')
        code_lbl.pack(anchor=tk.W, padx=5, pady=5)
        self.code_entry = ttk.Entry(self.tr_lblframe)
        self.code_entry.pack(fill=tk.X, padx=5, pady=5)

        name_lbl = ttk.Label(self.tr_lblframe, text='Item Name:')
        name_lbl.pack(anchor=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.tr_lblframe)
        self.name_entry.pack(fill=tk.X, padx=5, pady=5)

        unit_lbl = ttk.Label(self.tr_lblframe, text='Unit:')
        unit_lbl.pack(anchor=tk.W, padx=5, pady=5)
        unit_of_measure = []
        session = DBSession()
        records = session.query(Units).all()
        for record in records:
            unit_of_measure.append(record.code)
        session.close()
        self.unit_var = tk.StringVar()
        self.unit_var.set('NOS')
        self.unit_cb = ttk.Combobox(self.tr_lblframe, values=unit_of_measure, textvariable=self.unit_var)
        self.unit_cb.pack(fill=tk.X, padx=5, pady=5)

        price_lbl = ttk.Label(self.tr_lblframe, text='Price:')
        price_lbl.pack(anchor=tk.W, padx=5, pady=5)
        self.price_entry = ttk.Entry(self.tr_lblframe)
        self.price_entry.pack(fill=tk.X, padx=5, pady=5)

        self.save_btn = ttk.Button(self.tr_lblframe, text='Save', image=self.img16_list['save'], compound=tk.LEFT)
        self.save_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.save_btn.config(command=self.save_record)

        self.edit_btn = ttk.Button(self.tr_lblframe, text='Edit', image=self.img16_list['edit'], compound=tk.LEFT)
        self.edit_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.edit_btn.config(command=self.edit_record)

        self.del_btn = ttk.Button(self.tr_lblframe, text='Delete', image=self.img16_list['minus'], compound=tk.LEFT)
        self.del_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.del_btn.config(command=self.delete_record)

        self.product_view = ttk.Treeview(top_frame)
        self.product_view.pack(
                            expand=True, fill=tk.BOTH,
                            side=tk.LEFT, padx=5, pady=5)
        self.product_view['columns'] = ('code', 'name', 'unit', 'price')
        self.product_view.heading('#0', text='Id')
        self.product_view.heading('code', text='Code')
        self.product_view.heading('name', text='Name')
        self.product_view.heading('unit', text='Unit')
        self.product_view.heading('price', text='Price')
        self.product_view.column('#0', width=60, stretch=False)
        self.product_view.column('unit', width=50, stretch=False)
        self.product_view.column('code', width=120, stretch=False)
        self.product_view.column('price', width=80, stretch=False, anchor=tk.E)

        self.vbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.LEFT, fill=tk.Y)

        self.vbar.config(command=self.product_view.yview)
        self.product_view['yscrollcommand'] = self.vbar.set

        self.product_view.tag_configure("odd", background="#d5f4e6")
        self.product_view.tag_configure("even", background="#80ced6")

        self.close_btn = ttk.Button(bot_frame, text='Close', image=self.img16_list['cancel'], compound=tk.LEFT)
        self.close_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.close_btn.config(command=self.close_app)
        self.update_view()
        self.code_entry.focus_set()

    def update_view(self):
        session = DBSession()
        records = session.query(Products).options(joinedload(Products.units)).all()
        if len(records) == 0:
            print('Sorry no records has been found.')
            session.close()
            return

        children = self.product_view.get_children()
        if len(children) != 0:
            for child in children:
                self.product_view.delete(child)
        counter = 1
        for record in records:
            values = (record.code, record.name, record.units.code, f'{record.price:,.2f}')
            if counter % 2 == 0:
                self.product_view.insert('', tk.END, str(record.id), text=str(record.id), tags='odd', values=values)
            else:
                self.product_view.insert('', tk.END, str(record.id), text=str(record.id), tags='even', values=values)
            counter+=1
        session.close()

    def search_record(self):
        item = self.search_entry.get()
        if item == '':
            mb.showwarning('No record', 'No records')
            self.search_entry.focus_set()
            return
        elif item == 'all':
            self.update_view()
            self.search_entry.focus_set()
            return
        session = DBSession()
        records = session.query(Products).join(Units).filter(Products.name.like(f'%{item}%')).all()
        if len(records) == 0:
            mb.showwarning('No record', 'No records')
            session.close()
            return
        children = self.product_view.get_children()
        self.product_view.delete(*children)
        counter = 1
        for record in records:
            values = (record.code, record.name, record.units.code, record.price)
            if counter % 2 == 0:
                self.product_view.insert('', tk.END, str(counter), text=str(counter), tags='even', values=values)
            else:
                self.product_view.insert('', tk.END, str(counter), text=str(counter), tags='odd', values=values)
            counter += 1
        session.close()

    def search_event(self, event):
        self.search_record()

    def save_record(self):
        code = self.code_entry.get()
        name = self.name_entry.get()
        price = self.price_entry.get()
        unit = self.unit_var.get()
        if (code == '') or (name == '') or (price == ''):
            mb.showwarning('Incomplete Data', 'Sorry missing data, \n record cannot be save.')
            self.code_entry.focus_set()
            return
        session = DBSession()
        if self.record_id == None:
            unit_record = session.query(Units).filter(Units.code == unit).first()
            new_record = Products(code=code, name=name, units=unit_record, price=float(price))
            session.add(new_record)
        else:
            record = session.query(Products).filter(Products.id == self.record_id).first()
            unit_record = session.query(Units).filter(Units.code == unit).first()
            record.code = code
            record.name = name
            record.units = unit_record
            record.price = float(price)
            self.record_id = None
        session.commit()
        session.close()
        self.code_entry.delete('0', tk.END)
        self.name_entry.delete('0', tk.END)
        self.price_entry.delete('0', tk.END)
        self.unit_var.set('NOS')
        self.update_view()
        self.code_entry.focus_set()

    def edit_record(self):
        select_unit = self.product_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        self.record_id = record_id
        session = DBSession()
        record = session.query(Products).filter(Products.id == record_id).first()
        self.code_entry.delete('0', tk.END)
        self.name_entry.delete('0', tk.END)
        self.price_entry.delete('0', tk.END)
        code = record.code
        name = record.name
        unit = record.units.code
        price = str(record.price)
        self.code_entry.insert(tk.END, code)
        self.name_entry.insert(tk.END, name)
        self.unit_var.set(unit)
        self.price_entry.insert(tk.END, price)
        session.close()
        self.code_entry.focus_set()

    def delete_record(self):
        select_unit = self.product_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        session = DBSession()
        record = session.query(Products).filter(Products.id == record_id).first()
        answer = mb.askyesno('Delete?', 'Are you sure you want to delete?')
        if answer:
            session.delete(record)
            session.commit()
        session.close()
        self.update_view()
        self.code_entry.focus_set()

    def close_app(self):
        self.master.destroy()
# End of ProductWindow Class

# Start of ProjectWindow class
class ProjectWindow(ttk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super(ProjectWindow, self).__init__(master, *args, **kwargs)
        self.master.protocol('WM_DELETE_WINDOW', self.close_app)
        self.master.title('Projects')
        self.master.geometry('800x400')
        self.img16_list = image_list()
        self.style = ttk.Style()
        self.record_id = None
        if os.name == "nt":
            self.master.iconbitmap('inventory.ico')
        self.setup_ui()

    def setup_ui(self):
        self.style.configure('Custom.TLabel', font='Times 24 italic', foreground='#911818')
        title_lbl = ttk.Label(self, text='Projects', style='Custom.TLabel')
        title_lbl.pack(fill=tk.X, padx=5, pady=5)

        top_frame = ttk.Frame(self)
        top_frame.pack(expand=True, fill=tk.BOTH)
        bot_frame = ttk.Frame(self)
        bot_frame.pack(fill=tk.X)

        self.tr_lblframe = ttk.LabelFrame(top_frame, text='Transaction')
        self.tr_lblframe.pack(
                            side=tk.LEFT, ipadx=10, ipady=10,
                            expand=True, fill=tk.BOTH, padx=5, pady=5)

        unit_lbl = ttk.Label(self.tr_lblframe, text='Project Code:')
        unit_lbl.pack(anchor=tk.W, padx=5, pady=5)
        self.code_entry = ttk.Entry(self.tr_lblframe)
        self.code_entry.pack(fill=tk.X, padx=5, pady=5)

        name_lbl = ttk.Label(self.tr_lblframe, text='Project Name:')
        name_lbl.pack(anchor=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.tr_lblframe)
        self.name_entry.pack(fill=tk.X, padx=5, pady=5)

        self.save_btn = ttk.Button(self.tr_lblframe, text='Save', image=self.img16_list['save'], compound=tk.LEFT)
        self.save_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.save_btn.config(command=self.save_record)

        self.edit_btn = ttk.Button(self.tr_lblframe, text='Edit', image=self.img16_list['edit'], compound=tk.LEFT)
        self.edit_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.edit_btn.config(command=self.edit_record)

        self.del_btn = ttk.Button(self.tr_lblframe, text='Delete', image=self.img16_list['minus'], compound=tk.LEFT)
        self.del_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.del_btn.config(command=self.delete_record)

        self.proj_view = ttk.Treeview(top_frame)
        self.proj_view.pack(
                            expand=True, fill=tk.BOTH,
                            side=tk.LEFT, padx=5, pady=5)
        self.proj_view['columns'] = ('code', 'name')
        self.proj_view.heading('#0', text='Id')
        self.proj_view.heading('code', text='Code')
        self.proj_view.heading('name', text='Name')
        self.proj_view.column('#0', width=50, stretch=False)
        self.proj_view.column('code', width=50, stretch=False)

        self.vbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.LEFT, fill=tk.Y)

        self.vbar.config(command=self.proj_view.yview)
        self.proj_view['yscrollcommand'] = self.vbar.set

        self.proj_view.tag_configure("odd", background="#d5f4e6")
        self.proj_view.tag_configure("even", background="#80ced6")

        self.close_btn = ttk.Button(bot_frame, text='Close', image=self.img16_list['cancel'], compound=tk.LEFT)
        self.close_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.close_btn.config(command=self.close_app)
        self.update_view()
        self.code_entry.focus_set()

    def update_view(self):
        session = DBSession()
        records = session.query(Projects).all()
        if len(records) == 0:
            print('Sorry no records has been found.')
            session.close()
            return

        children = self.proj_view.get_children()
        if len(children) != 0:
            for child in children:
                self.proj_view.delete(child)
        counter = 1
        for record in records:
            if counter % 2 == 0:
                self.proj_view.insert('', tk.END, str(record.id), text=str(record.id), tags='odd')
            else:
                self.proj_view.insert('', tk.END, str(record.id), text=str(record.id), tags='even')
            self.proj_view.set(str(record.id), 'code', record.code)
            self.proj_view.set(str(record.id), 'name', record.name)
            counter+=1
        session.close()

    def save_record(self):
        code = self.code_entry.get()
        name = self.name_entry.get()
        if (code == '') or (name == ''):
            mb.showwarning('Incomplete Data', 'Sorry missing data, \n record cannot be save.')
            self.code_entry.focus_set()
            return
        session = DBSession()
        if self.record_id == None:
            new_record = Projects(code=code, name=name)
            session.add(new_record)
        else:
            record = session.query(Projects).filter(Projects.id == self.record_id).first()
            record.code = code
            record.name = name
            self.record_id = None
        session.commit()
        session.close()
        self.code_entry.delete('0', tk.END)
        self.name_entry.delete('0', tk.END)
        self.update_view()
        self.code_entry.focus_set()

    def edit_record(self):
        select_unit = self.proj_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        self.record_id = record_id
        session = DBSession()
        record = session.query(Projects).filter(Projects.id == record_id).first()
        self.code_entry.delete('0', tk.END)
        self.name_entry.delete('0', tk.END)
        code = record.code
        name = record.name
        self.code_entry.insert(tk.END, code)
        self.name_entry.insert(tk.END, name)
        session.close()
        self.code_entry.focus_set()

    def delete_record(self):
        select_unit = self.proj_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        session = DBSession()
        record = session.query(Projects).filter(Projects.id == record_id).first()
        answer = mb.askyesno('Delete?', 'Are you sure you want to delete?')
        if answer:
            session.delete(record)
            session.commit()
        session.close()
        self.update_view()
        self.code_entry.focus_set()

    def close_app(self):
        self.master.destroy()
# End of ProjectWindow class

# Start of SupplierWindow class
class SupplierWindow(ttk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super(SupplierWindow, self).__init__(master, *args, **kwargs)
        self.master.protocol('WM_DELETE_WINDOW', self.close_app)
        self.master.title('Suppliers')
        self.master.geometry('800x400')
        self.img16_list = image_list()
        self.style = ttk.Style()
        self.record_id = None
        if os.name == "nt":
            self.master.iconbitmap('inventory.ico')
        self.setup_ui()

    def setup_ui(self):
        self.style.configure('Custom.TLabel', font='Times 24 italic', foreground='#911818')
        title_lbl = ttk.Label(self, text='Suppliers', style='Custom.TLabel')
        title_lbl.pack(fill=tk.X, padx=5, pady=5)

        top_frame = ttk.Frame(self)
        top_frame.pack(expand=True, fill=tk.BOTH)
        bot_frame = ttk.Frame(self)
        bot_frame.pack(fill=tk.X)

        self.tr_lblframe = ttk.LabelFrame(top_frame, text='Transaction')
        self.tr_lblframe.pack(
                            side=tk.LEFT, ipadx=10, ipady=10,
                            expand=True, fill=tk.BOTH, padx=5, pady=5)

        unit_lbl = ttk.Label(self.tr_lblframe, text='Supplier Code:')
        unit_lbl.pack(anchor=tk.W, padx=5, pady=5)
        self.code_entry = ttk.Entry(self.tr_lblframe)
        self.code_entry.pack(fill=tk.X, padx=5, pady=5)

        name_lbl = ttk.Label(self.tr_lblframe, text='Supplier Name:')
        name_lbl.pack(anchor=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.tr_lblframe)
        self.name_entry.pack(fill=tk.X, padx=5, pady=5)

        self.save_btn = ttk.Button(self.tr_lblframe, text='Save', image=self.img16_list['save'], compound=tk.LEFT)
        self.save_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.save_btn.config(command=self.save_record)

        self.edit_btn = ttk.Button(self.tr_lblframe, text='Edit', image=self.img16_list['edit'], compound=tk.LEFT)
        self.edit_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.edit_btn.config(command=self.edit_record)

        self.del_btn = ttk.Button(self.tr_lblframe, text='Delete', image=self.img16_list['minus'], compound=tk.LEFT)
        self.del_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.del_btn.config(command=self.delete_record)

        self.supp_view = ttk.Treeview(top_frame)
        self.supp_view.pack(
                            expand=True, fill=tk.BOTH,
                            side=tk.LEFT, padx=5, pady=5)
        self.supp_view['columns'] = ('code', 'name')
        self.supp_view.heading('#0', text='Id')
        self.supp_view.heading('code', text='Code')
        self.supp_view.heading('name', text='Name')
        self.supp_view.column('#0', width=50, stretch=False)
        self.supp_view.column('code', width=50, stretch=False)

        self.vbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.LEFT, fill=tk.Y)

        self.vbar.config(command=self.supp_view.yview)
        self.supp_view['yscrollcommand'] = self.vbar.set

        self.supp_view.tag_configure("odd", background="#d5f4e6")
        self.supp_view.tag_configure("even", background="#80ced6")

        self.close_btn = ttk.Button(bot_frame, text='Close', image=self.img16_list['cancel'], compound=tk.LEFT)
        self.close_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.close_btn.config(command=self.close_app)
        self.update_view()
        self.code_entry.focus_set()

    def update_view(self):
        session = DBSession()
        records = session.query(Suppliers).all()
        if len(records) == 0:
            print('Sorry no records has been found.')
            session.close()
            return

        children = self.supp_view.get_children()
        if len(children) != 0:
            for child in children:
                self.supp_view.delete(child)
        counter = 1
        for record in records:
            if counter % 2 == 0:
                self.supp_view.insert('', tk.END, str(record.id), text=str(record.id), tags='odd')
            else:
                self.supp_view.insert('', tk.END, str(record.id), text=str(record.id), tags='even')
            self.supp_view.set(str(record.id), 'code', record.code)
            self.supp_view.set(str(record.id), 'name', record.name)
            counter+=1
        session.close()

    def save_record(self):
        code = self.code_entry.get()
        name = self.name_entry.get()
        if (code == '') or (name == ''):
            mb.showwarning('Incomplete Data', 'Sorry missing data, \n record cannot be save.')
            self.code_entry.focus_set()
            return
        session = DBSession()
        if self.record_id == None:
            new_record = Suppliers(code=code, name=name)
            session.add(new_record)
        else:
            record = session.query(Suppliers).filter(Suppliers.id == self.record_id).first()
            record.code = code
            record.name = name
            self.record_id = None
        session.commit()
        session.close()
        self.code_entry.delete('0', tk.END)
        self.name_entry.delete('0', tk.END)
        self.update_view()
        self.code_entry.focus_set()

    def edit_record(self):
        select_unit = self.supp_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        self.record_id = record_id
        session = DBSession()
        record = session.query(Suppliers).filter(Suppliers.id == record_id).first()
        self.code_entry.delete('0', tk.END)
        self.name_entry.delete('0', tk.END)
        code = record.code
        name = record.name
        self.code_entry.insert(tk.END, code)
        self.name_entry.insert(tk.END, name)
        session.close()
        self.code_entry.focus_set()

    def delete_record(self):
        select_unit = self.supp_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        session = DBSession()
        record = session.query(Projects).filter(Projects.id == record_id).first()
        answer = mb.askyesno('Delete?', 'Are you sure you want to delete?')
        if answer:
            session.delete(record)
            session.commit()
        session.close()
        self.update_view()
        self.code_entry.focus_set()

    def close_app(self):
        self.master.destroy()
# End of SupplierWindow class

# Start of CalendarWidget class
class CalendarWidget(tk.Frame):

    def __init__(self, year, month, master=None, **kws):
        super(CalendarWidget, self).__init__(master, **kws)
        self.year = year
        self.month = month
        self.date = None
        self.cal = cl.Calendar(6)
        self.master.protocol("WM_DELETE_WINDOW", self.close)
        self.master.title("Calendar")
        self.master.resizable(False, False)
        if os.name == "nt":
            self.master.iconbitmap('inventory.ico')
        self.setup_ui()

    def setup_ui(self):
        container = tk.Frame(self)
        container.pack(expand=True, fill=tk.BOTH)

        self.prev_btn = tk.Button(container, text="<",
                                  font="Times 12 bold", fg="blue", bg="white")
        self.prev_btn.pack(side=tk.LEFT, fill="y")
        self.prev_btn.bind("<Button-1>", self.btnHandler)

        self.month_var = tk.StringVar()
        self.month_lbl = tk.Label(container, textvariable=self.month_var,
                                  font="Times 14 bold", fg="blue", bg="white")
        self.month_lbl.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.next_btn = tk.Button(container, text=">",
                                  font="Times 12 bold", fg="blue", bg="white")
        self.next_btn.pack(side=tk.LEFT, fill="y")
        self.next_btn.bind("<Button-1>", self.btnHandler)

        self.days_frame = tk.Frame(self)
        self.days_frame.pack(expand=True, fill=tk.BOTH)

        self.updateCalendar()
        self.focus_set()

    def updateCalendar(self):
        children = self.days_frame.winfo_children()
        if len(children) != 0:
            for child in children:
                child.destroy()

        days = ["Sun", "Mon", "Tue",
                "Wed", "Thu", "Fri",
                "Sat"]
        month = ["January", "February", "March",
                 "April", "May", "June",
                 "July", "August", "September",
                 "October", "November", "December"]

        self.month_var.set(month[self.month-1]+" "+str(self.year))
        list_of_days = self.cal.monthdayscalendar(self.year, self.month)
        list_of_days.insert(0, days)

        for idx, week in enumerate(list_of_days):
            for idx1, day in enumerate(week):
                if day == 0:
                    self.day_lbl = tk.Label(self.days_frame, text=str(""),
                                            relief=tk.RAISED,
                                            state="disabled",
                                            font="Times 12 normal",
                                            bg="white")
                    self.day_lbl.grid(row=idx, column=idx1, sticky="nesw")
                elif day in days:
                    self.day_lbl = tk.Label(self.days_frame,
                                            text=str(day), relief=tk.RAISED,
                                            font="Times 12 bold")
                    self.day_lbl.grid(row=idx, column=idx1, sticky="nesw")
                    if (day == "Sun") or (day == "Sat"):
                        self.day_lbl.config(fg="red")
                else:
                    self.day_btn = tk.Button(self.days_frame, text=str(day),
                                             width=3, font="Times 12 normal",
                                             bg="white")
                    self.day_btn.grid(row=idx, column=idx1, sticky="nesw")
                    self.day_btn.bind("<Button-1>", self.printEvent)
                    if (idx1 == 0) or (idx1 == 6):
                        self.day_btn.config(fg='red')

    def printEvent(self, event):
        if event.widget.winfo_class() == "Button":
            day = event.widget.cget("text")
            self.date = "%s/%s/%s" % ("{:02}".format(int(day)),
                                      "{:02}".format(self.month),
                                      str(self.year))
            # self.date = f"{day:02}/{self.month:02}/{self.year:02}"
            self.close()

    def btnHandler(self, event):
        if event.widget.cget('text') == "<":
            if (self.month - 1) == 0:
                self.month = 12
                self.year = self.year - 1
                self.updateCalendar()
            else:
                self.month = self.month - 1
                self.updateCalendar()
        elif event.widget.cget('text') == ">":
            if (self.month + 1) > 12:
                self.month = 1
                self.year = self.year + 1
                self.updateCalendar()
            else:
                self.month = self.month + 1
                self.updateCalendar()

    def close(self):
        self.master.destroy()
# End of CalendarWidget class.

# Start of IncomingWindow class
class IncomingWindow(ttk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super(IncomingWindow, self).__init__(master, *args, **kwargs)
        self.master.protocol('WM_DELETE_WINDOW', self.close_app)
        self.master.title('Incoming')
        # self.master.geometry('800x600+20+20')
        self.img16_list = image_list()
        self.style = ttk.Style()
        self.record_id = None
        if os.name == "nt":
            self.master.state("zoomed")
            self.master.iconbitmap('inventory.ico')
        self.setup_ui()

    def setup_ui(self):
        self.style.configure('Custom.TLabel', font='Times 24 italic', foreground='#911818')

        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(title_frame, text='Incoming', style='Custom.TLabel')
        title_lbl.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)

        self.search_entry = ttk.Entry(title_frame, width=40)
        self.search_entry.pack(side=tk.RIGHT, padx=5, pady=5)
        self.search_entry.bind('<KeyPress-Return>', self.search_event)

        self.search_btn = ttk.Button(title_frame, text='Search', image=self.img16_list['search'], compound=tk.LEFT)
        self.search_btn.pack(side=tk.RIGHT)
        self.search_btn.config(command=self.search_record)

        top_frame = ttk.Frame(self)
        top_frame.pack(expand=True, fill=tk.BOTH)
        bot_frame = ttk.Frame(self)
        bot_frame.pack(fill=tk.X)

        self.tr_lblframe = ttk.LabelFrame(top_frame, text='Transaction')
        self.tr_lblframe.pack(
                            side=tk.LEFT, ipadx=10, ipady=10,
                            expand=True, fill=tk.BOTH, padx=5, pady=5)

        date_lbl = ttk.Label(self.tr_lblframe, text='Date:')
        date_lbl.grid(row=0, column=0, pady=5, padx=5, sticky='we')
        self.date_entry = ttk.Entry(self.tr_lblframe)
        self.date_entry.grid(row=1, column=0, pady=5, padx=5, sticky='we', columnspan=2)
        self.date_entry.insert(tk.END, datetime.strftime(datetime.today(), '%d/%m/%Y'))
        self.date_btn = ttk.Button(self.tr_lblframe, image=self.img16_list['calendar'])
        self.date_btn.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.date_btn.config(command=self.change_date)

        supp_lbl = ttk.Label(self.tr_lblframe, text='Supplier:')
        supp_lbl.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)

        supp_list = []
        self.supp_var = tk.StringVar()
        session = DBSession()
        supp_records = session.query(Suppliers).all()
        for supp_record in supp_records:
            supp_list.append(supp_record.name)
        self.supp_var.set(supp_list[0])
        self.supp_cb = ttk.Combobox(self.tr_lblframe, values=supp_list, textvariable=self.supp_var)
        self.supp_cb.grid(row=3, column=0, pady=5, padx=5, sticky='we', columnspan=2)

        code_lbl = ttk.Label(self.tr_lblframe, text='Product Code:')
        code_lbl.grid(row=4, column=0, pady=5, padx=5, sticky=tk.W)
        self.code_entry = ttk.Entry(self.tr_lblframe)
        self.code_entry.grid(row=5, column=0, pady=5, padx=5, sticky='we', columnspan=2)

        self.code_entry.bind('<KeyPress-Return>', self.validate_item_code)

        name_lbl = ttk.Label(self.tr_lblframe, text='Product Name:')
        name_lbl.grid(row=6, column=0, pady=5, padx=5, sticky=tk.W)
        self.name_entry = ttk.Entry(self.tr_lblframe)
        self.name_entry.grid(row=7, column=0, pady=5, padx=5, sticky='we', columnspan=2)

        bin_lbl = ttk.Label(self.tr_lblframe, text='Bin Location:')
        bin_lbl.grid(row=8, column=0, pady=5, padx=5, sticky=tk.W)

        self.bin_entry = ttk.Entry(self.tr_lblframe)
        self.bin_entry.grid(row=9, column=0, pady=5, padx=5, sticky='we', columnspan=2)

        self.bin_entry.bind('<KeyPress-Return>', self.validate_location)

        unit_lbl = ttk.Label(self.tr_lblframe, text='Unit')
        unit_lbl.grid(row=10, column=0, sticky=tk.W, pady=5, padx=5,)
        self.unit_entry = ttk.Entry(self.tr_lblframe)
        self.unit_entry.grid(row=11, column=0, sticky='we', columnspan=2)

        qty_lbl = ttk.Label(self.tr_lblframe, text='Quantity:')
        qty_lbl.grid(row=12, column=0, sticky=tk.W, pady=5, padx=5,)
        self.qty_entry = ttk.Entry(self.tr_lblframe)
        self.qty_entry.grid(row=13, column=0, sticky='we', columnspan=2)

        rema_lbl = ttk.Label(self.tr_lblframe, text='Remarks:')
        rema_lbl.grid(row=14, column=0, sticky=tk.W, pady=5, padx=5,)
        self.rema_entry = ttk.Entry(self.tr_lblframe)
        self.rema_entry.grid(row=15, column=0, sticky='we', columnspan=2)

        self.save_btn = ttk.Button(self.tr_lblframe, text='Save', image=self.img16_list['save'], compound=tk.LEFT)
        self.save_btn.grid(row=16, column=0, padx=5, pady=5, sticky=tk.E)
        self.save_btn.config(command=self.save_record)

        self.edit_btn = ttk.Button(self.tr_lblframe, text='Edit', image=self.img16_list['edit'], compound=tk.LEFT)
        self.edit_btn.grid(row=16, column=1, padx=5, pady=5, sticky=tk.E)
        self.edit_btn.config(command=self.edit_record)

        self.del_btn = ttk.Button(self.tr_lblframe, text='Delete', image=self.img16_list['minus'], compound=tk.LEFT)
        self.del_btn.grid(row=16, column=2, padx=5, pady=5, sticky=tk.E)
        self.del_btn.config(command=self.delete_record)

        self.incg_view = ttk.Treeview(top_frame)
        self.incg_view.pack(
                            expand=True, fill=tk.BOTH,
                            side=tk.LEFT, padx=5, pady=5)
        self.incg_view['columns'] = ('date', 'code', 'name', 'unit', 'price', 'quantity', 'bin', 'remarks')
        self.incg_view.heading('#0', text='Id')
        self.incg_view.heading('date', text='Date')
        self.incg_view.heading('code', text='Item Code')
        self.incg_view.heading('name', text='Description')
        self.incg_view.heading('unit', text='Unit')
        self.incg_view.heading('price', text='Price')
        self.incg_view.heading('quantity', text='Quantity')
        self.incg_view.heading('bin', text='Bin')
        self.incg_view.heading('remarks', text='Remarks')
        self.incg_view.column('#0', width=60, stretch=False)
        self.incg_view.column('unit', width=50, stretch=False)
        self.incg_view.column('code', width=120, stretch=False)
        self.incg_view.column('price', width=80, stretch=False, anchor=tk.E)
        self.incg_view.column('quantity', width=80, stretch=False)
        self.incg_view.column('bin', width=80, stretch=False)
        self.incg_view.column('date', width=80, stretch=False)

        self.vbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.LEFT, fill=tk.Y)

        self.vbar.config(command=self.incg_view.yview)
        self.incg_view['yscrollcommand'] = self.vbar.set

        self.incg_view.tag_configure("odd", background="#d5f4e6")
        self.incg_view.tag_configure("even", background="#80ced6")

        self.close_btn = ttk.Button(bot_frame, text='Close', image=self.img16_list['cancel'], compound=tk.LEFT)
        self.close_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.close_btn.config(command=self.close_app)
        session.close()
        self.update_view()
        self.date_entry.focus_set()

    def validate_item_code(self, event):
        item_code = self.code_entry.get()
        session = DBSession()
        record = session.query(Products).options(joinedload(Products.units)).filter(Products.code == item_code).first()
        if not record:
            mb.showwarning('Invalid Item', 'Sorry the item code you entered is invalid.\n Please try again.')
            self.code_entry.focus_set()
        else:
            self.name_entry.delete('0', tk.END)
            self.name_entry.insert(tk.END, record.name)
            self.unit_entry.delete('0', tk.END)
            self.unit_entry.insert(tk.END, record.units.code)
            self.qty_entry.focus_set()
        session.close()

    def validate_location(self, event):
        location = self.bin_entry.get()
        session = DBSession()
        record = session.query(BinLocation).filter(BinLocation.code == location).first()
        if not record:
            mb.showwarning('Invalid Location', 'Sorry the location you entered is invalid.\n Please try again.')
            self.bin_entry.focus_set()
        else:
            self.qty_entry.focus_set()
        session.close()

    def search_record(self):
        item = self.search_entry.get()
        if item == '':
            mb.showwarning('No records', 'No records')
            self.search_entry.focus_set()
            return
        elif item == 'all':
            self.update_view()
            return
        session = DBSession()
        records = session.query(Incoming).join(Products, BinLocation).filter(Products.name.like(f'%{item}%')).all()
        if len(records) == 0:
            mb.showwarning('No records', 'No records')
            session.close()
            self.search_entry.focus_set()
            return
        counter = 1
        children = self.incg_view.get_children()
        self.incg_view.delete(*children)
        for record in records:
            values = (record.in_date, record.products.code, record.name,
                    record.products.units.code, record.products.price, record.quantity,
                    record.binlocation.code, record.remarks)
            if counter % 2 == 0:
                self.incg_view.insert('', tk.END, str(record.id), text=str(record.id), tags='even', values=values)
            else:
                self.incg_view.insert('', tk.END, str(record.id), text=str(record.id), tags='odd', values=values)
            counter += 1
        session.close()

    def search_event(self, event):
        self.search_record()

    def update_view(self):
        session = DBSession()
        records = session.query(Incoming).options(joinedload(Incoming.products),
                                                joinedload(Incoming.binlocation),
                                                joinedload(Incoming.suppliers)).all()
        if len(records) == 0:
            session.close()
            return

        children = self.incg_view.get_children()
        if len(children) != 0:
            for child in children:
                self.incg_view.delete(child)
        counter = 1
        for record in records:
            if counter % 2 == 0:
                self.incg_view.insert('', tk.END, str(record.id), text=str(record.id), tags='odd')
            else:
                self.incg_view.insert('', tk.END, str(record.id), text=str(record.id), tags='even')
            self.incg_view.set(str(record.id), 'date', datetime.strftime(record.in_date, '%d/%m/%Y'))
            self.incg_view.set(str(record.id), 'code', record.products.code)
            self.incg_view.set(str(record.id), 'name', record.products.name)
            self.incg_view.set(str(record.id), 'unit', record.products.units.code)
            self.incg_view.set(str(record.id), 'price', f'{record.products.price:,.2f}')
            self.incg_view.set(str(record.id), 'quantity', f'{record.quantity}')
            self.incg_view.set(str(record.id), 'bin', record.binlocation.code)
            self.incg_view.set(str(record.id), 'remarks', record.remarks)
            counter+=1
        session.close()

    def save_record(self):
        in_date = datetime.strptime(self.date_entry.get(), '%d/%m/%Y')
        code = self.code_entry.get()
        name = self.name_entry.get()
        binloc = self.bin_entry.get()
        quantity = float(self.qty_entry.get())
        remarks = self.rema_entry.get()
        supp_name = self.supp_var.get()
        if (name == '') or (quantity == ''):
            mb.showwarning('Incomplete Data', 'Sorry missing data, \n record cannot be save.')
            self.code_entry.focus_set()
            return
        session = DBSession()
        if self.record_id == None:
            prod_record = session.query(Products).filter(Products.code == code).first()
            bin_record = session.query(BinLocation).filter(BinLocation.code == binloc).first()
            supp_record = session.query(Suppliers).filter(Suppliers.name == supp_name).first()
            new_record = Incoming(in_date=in_date, suppliers=supp_record,
                                products=prod_record, binlocation=bin_record,
                                name=name, quantity=quantity, remarks=remarks)
            session.add(new_record)
        else:
            record = session.query(Incoming).filter(Incoming.id == self.record_id).first()
            prod_record = session.query(Products).filter(Products.code == code).first()
            bin_record = session.query(BinLocation).filter(BinLocation.code == binloc).first()
            supp_record = session.query(Suppliers).filter(Suppliers.name == supp_name).first()
            record.in_date = in_date
            record.suppliers = supp_record
            record.products = prod_record
            record.binlocation = bin_record
            record.name = name
            record.quantity = quantity
            record.remarks = remarks
            self.record_id = None
        session.commit()
        session.close()
        self.code_entry.delete('0', tk.END)
        self.bin_entry.delete('0', tk.END)
        self.name_entry.delete('0', tk.END)
        self.qty_entry.delete('0', tk.END)
        self.rema_entry.delete('0', tk.END)
        self.update_view()
        self.code_entry.focus_set()

    def edit_record(self):
        select_unit = self.incg_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        self.record_id = record_id
        session = DBSession()
        record = session.query(Incoming).filter(Incoming.id == record_id).first()
        self.code_entry.delete('0', tk.END)
        self.bin_entry.delete('0', tk.END)
        self.name_entry.delete('0', tk.END)
        self.date_entry.delete('0', tk.END)
        self.unit_entry.delete('0', tk.END)
        self.qty_entry.delete('0', tk.END)
        self.rema_entry.delete('0', tk.END)

        in_date = datetime.strftime(record.in_date, '%d/%m/%Y')
        supplier = record.suppliers.name
        code = record.products.code
        unit = record.products.units.code
        name = record.name
        location = record.binlocation.code
        quantity = str(record.quantity)
        remarks = record.remarks

        self.date_entry.insert(tk.END, in_date)
        self.supp_var.set(supplier)
        self.code_entry.insert(tk.END, code)
        self.name_entry.insert(tk.END, name)
        self.bin_entry.insert(tk.END, location)
        self.unit_entry.insert(tk.END, unit)
        self.qty_entry.insert(tk.END, quantity)
        self.rema_entry.insert(tk.END, remarks)

        session.close()
        self.code_entry.focus_set()

    def delete_record(self):
        select_unit = self.incg_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        session = DBSession()
        record = session.query(Incoming).filter(Incoming.id == record_id).first()
        answer = mb.askyesno('Delete?', 'Are you sure you want to delete?')
        if answer:
            session.delete(record)
            session.commit()
        session.close()
        self.update_view()
        self.code_entry.focus_set()

    def change_date(self):
        date_today = datetime.today()
        tp = tk.Toplevel(self)
        win = CalendarWidget(date_today.year, date_today.month, tp)
        win.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.wait_window(tp)
        if win.date is not None:
            self.date_entry.delete('0', tk.END)
            self.date_entry.insert(tk.END, win.date)
            # self.update_view()

    def close_app(self):
        self.master.destroy()
# End of IncomingWindow class

# Start of OutgoingWindow class
class OutgoingWindow(ttk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super(OutgoingWindow, self).__init__(master, *args, **kwargs)
        self.master.protocol('WM_DELETE_WINDOW', self.close_app)
        self.master.title('Outgoing')
        # self.master.geometry('800x600+20+20')
        self.img16_list = image_list()
        self.style = ttk.Style()
        self.record_id = None
        if os.name == "nt":
            self.master.state("zoomed")
            self.master.iconbitmap('inventory.ico')
        self.setup_ui()

    def setup_ui(self):
        self.style.configure('Custom.TLabel', font='Times 24 italic', foreground='#911818')

        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(title_frame, text='Outgoing', style='Custom.TLabel')
        title_lbl.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)

        self.search_entry = ttk.Entry(title_frame, width=40)
        self.search_entry.pack(side=tk.RIGHT, padx=5, pady=5)
        #self.search_entry.bind('<KeyPress-Return>', self.search_event)

        self.search_btn = ttk.Button(title_frame, text='Search', image=self.img16_list['search'], compound=tk.LEFT)
        self.search_btn.pack(side=tk.RIGHT)
        self.search_btn.config(command=self.search_record)

        top_frame = ttk.Frame(self)
        top_frame.pack(expand=True, fill=tk.BOTH)
        bot_frame = ttk.Frame(self)
        bot_frame.pack(fill=tk.X)

        self.tr_lblframe = ttk.LabelFrame(top_frame, text='Transaction')
        self.tr_lblframe.pack(
                            side=tk.LEFT, ipadx=10, ipady=10,
                            expand=True, fill=tk.BOTH, padx=5, pady=5)

        date_lbl = ttk.Label(self.tr_lblframe, text='Date:')
        date_lbl.grid(row=0, column=0, pady=5, padx=5, sticky='we')
        self.date_entry = ttk.Entry(self.tr_lblframe)
        self.date_entry.grid(row=1, column=0, pady=5, padx=5, sticky='we', columnspan=2)
        self.date_entry.insert(tk.END, datetime.strftime(datetime.today(), '%d/%m/%Y'))
        self.date_btn = ttk.Button(self.tr_lblframe, image=self.img16_list['calendar'])
        self.date_btn.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.date_btn.config(command=self.change_date)

        proj_lbl = ttk.Label(self.tr_lblframe, text='Project:')
        proj_lbl.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)

        proj_list = []
        self.proj_var = tk.StringVar()
        session = DBSession()
        proj_records = session.query(Projects).all()
        for proj_record in proj_records:
            proj_list.append(proj_record.name)
        self.proj_var.set(proj_list[0])
        self.proj_cb = ttk.Combobox(self.tr_lblframe, values=proj_list, textvariable=self.proj_var)
        self.proj_cb.grid(row=3, column=0, pady=5, padx=5, sticky='we', columnspan=2)

        code_lbl = ttk.Label(self.tr_lblframe, text='Product Code:')
        code_lbl.grid(row=4, column=0, pady=5, padx=5, sticky=tk.W)
        self.code_entry = ttk.Entry(self.tr_lblframe)
        self.code_entry.grid(row=5, column=0, pady=5, padx=5, sticky='we', columnspan=2)

        self.code_entry.bind('<KeyPress-Return>', self.validate_item_code)

        name_lbl = ttk.Label(self.tr_lblframe, text='Product Name:')
        name_lbl.grid(row=6, column=0, pady=5, padx=5, sticky=tk.W)
        self.name_entry = ttk.Entry(self.tr_lblframe)
        self.name_entry.grid(row=7, column=0, pady=5, padx=5, sticky='we', columnspan=2)

        bin_lbl = ttk.Label(self.tr_lblframe, text='Bin Location:')
        bin_lbl.grid(row=8, column=0, pady=5, padx=5, sticky=tk.W)

        listbox_frame = ttk.Frame(self.tr_lblframe)
        listbox_frame.grid(row=9, column=0, pady=5, padx=5, sticky='we', columnspan=2)

        self.bin_listbox = tk.Listbox(listbox_frame, height=5)
        self.bin_listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.listbox_sb = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        self.listbox_sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox_sb.config(command=self.bin_listbox.yview)
        self.bin_listbox['yscrollcommand'] = self.listbox_sb.set

        unit_lbl = ttk.Label(self.tr_lblframe, text='Unit')
        unit_lbl.grid(row=10, column=0, sticky=tk.W, pady=5, padx=5,)
        self.unit_entry = ttk.Entry(self.tr_lblframe)
        self.unit_entry.grid(row=11, column=0, sticky='we', columnspan=2)

        qty_lbl = ttk.Label(self.tr_lblframe, text='Quantity:')
        qty_lbl.grid(row=12, column=0, sticky=tk.W, pady=5, padx=5,)
        self.qty_entry = ttk.Entry(self.tr_lblframe)
        self.qty_entry.grid(row=13, column=0, sticky='we', columnspan=2)

        rema_lbl = ttk.Label(self.tr_lblframe, text='Remarks:')
        rema_lbl.grid(row=14, column=0, sticky=tk.W, pady=5, padx=5,)
        self.rema_entry = ttk.Entry(self.tr_lblframe)
        self.rema_entry.grid(row=15, column=0, sticky='we', columnspan=2)

        self.save_btn = ttk.Button(self.tr_lblframe, text='Save', image=self.img16_list['save'], compound=tk.LEFT)
        self.save_btn.grid(row=16, column=0, padx=5, pady=5, sticky=tk.E)
        self.save_btn.config(command=self.save_record)

        self.edit_btn = ttk.Button(self.tr_lblframe, text='Edit', image=self.img16_list['edit'], compound=tk.LEFT)
        self.edit_btn.grid(row=16, column=1, padx=5, pady=5, sticky=tk.E)
        self.edit_btn.config(command=self.edit_record)

        self.del_btn = ttk.Button(self.tr_lblframe, text='Delete', image=self.img16_list['minus'], compound=tk.LEFT)
        self.del_btn.grid(row=16, column=2, padx=5, pady=5, sticky=tk.E)
        self.del_btn.config(command=self.delete_record)

        self.outg_view = ttk.Treeview(top_frame)
        self.outg_view.pack(
                            expand=True, fill=tk.BOTH,
                            side=tk.LEFT, padx=5, pady=5)
        self.outg_view['columns'] = ('date', 'code', 'name', 'unit', 'price', 'quantity', 'bin', 'remarks')
        self.outg_view.heading('#0', text='Id')
        self.outg_view.heading('date', text='Date')
        self.outg_view.heading('code', text='Item Code')
        self.outg_view.heading('name', text='Description')
        self.outg_view.heading('unit', text='Unit')
        self.outg_view.heading('price', text='Price')
        self.outg_view.heading('quantity', text='Quantity')
        self.outg_view.heading('bin', text='Bin')
        self.outg_view.heading('remarks', text='Remarks')
        self.outg_view.column('#0', width=60, stretch=False)
        self.outg_view.column('unit', width=50, stretch=False)
        self.outg_view.column('code', width=120, stretch=False)
        self.outg_view.column('price', width=80, stretch=False, anchor=tk.E)
        self.outg_view.column('quantity', width=80, stretch=False)
        self.outg_view.column('bin', width=80, stretch=False)
        self.outg_view.column('date', width=80, stretch=False)

        self.vbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.LEFT, fill=tk.Y)

        self.vbar.config(command=self.outg_view.yview)
        self.outg_view['yscrollcommand'] = self.vbar.set

        self.outg_view.tag_configure("odd", background="#d5f4e6")
        self.outg_view.tag_configure("even", background="#80ced6")

        self.close_btn = ttk.Button(bot_frame, text='Close', image=self.img16_list['cancel'], compound=tk.LEFT)
        self.close_btn.pack(anchor=tk.E, padx=5, pady=5)
        self.close_btn.config(command=self.close_app)
        session.close()
        self.update_view()
        self.code_entry.focus_set()

    def validate_item_code(self, event):
        item_code = self.code_entry.get()
        session = DBSession()
        record = session.query(Products).options(joinedload(Products.units)).filter(Products.code == item_code).first()
        if not record:
            mb.showwarning('Invalid Item', 'Sorry the item code you entered is invalid.\n Please try again.')
            self.code_entry.focus_set()
        else:
            self.name_entry.delete('0', tk.END)
            self.name_entry.insert(tk.END, record.name)
            self.unit_entry.delete('0', tk.END)
            self.unit_entry.insert(tk.END, record.units.code)
            self.qty_entry.focus_set()

        # This will check quantity in incoming & outgoing table
        incg_total = {}
        outg_total = {}
        incg_records = session.query(Incoming).options(joinedload(Incoming.products), joinedload(Incoming.binlocation)).filter(Incoming.products == record).all()
        outg_records = session.query(Outgoing).options(joinedload(Outgoing.products), joinedload(Outgoing.binlocation)).filter(Outgoing.products == record).all()
        for incg_record in incg_records:
            if incg_record.binlocation.code in incg_total.keys():
                incg_total[incg_record.binlocation.code]+=incg_record.quantity
            else:
                incg_total[incg_record.binlocation.code] = incg_record.quantity
        for outg_record in outg_records:
            if outg_record.binlocation.code in outg_total.keys():
                outg_total[outg_record.binlocation.code]+=outg_record.quantity
            else:
                outg_total[outg_record.binlocation.code] = outg_record.quantity

        for key, value in incg_total.items():
            if key in outg_total.keys():
                incg_total[key]+=outg_total[key]
                del outg_total[key]

        incg_total.update(outg_total)

        qty_avail = []
        for key, value in incg_total.items():
            qty_avail.append(f'{key} ==> {value}')
        if len(qty_avail) != 0:
            self.bin_listbox.insert(tk.END, *qty_avail)
            self.bin_listbox.select_set(0)
        session.close()

    def search_record(self):
        item = self.search_entry.get()
        if item == '':
            mb.showwarning('No records', 'No records')
            self.search_entry.focus_set()
            return
        elif item == 'all':
            self.update_view()
            return
        session = DBSession()
        records = session.query(Outgoing).join(Products, BinLocation).filter(Products.name.like(f'%{item}%')).all()
        if len(records) == 0:
            mb.showwarning('No records', 'No records')
            session.close()
            self.search_entry.focus_set()
            return
        counter = 1
        children = self.outg_view.get_children()
        self.outg_view.delete(*children)
        for record in records:
            values = (record.out_date, record.products.code, record.name,
                    record.products.units.code, record.products.price, record.quantity,
                    record.binlocation.code, record.remarks)
            if counter % 2 == 0:
                self.outg_view.insert('', tk.END, str(record.id), text=str(record.id), tags='even', values=values)
            else:
                self.outg_view.insert('', tk.END, str(record.id), text=str(record.id), tags='odd', values=values)
            counter += 1
        session.close()

    def search_event(self, event):
        self.search_record()

    def update_view(self):
        session = DBSession()
        records = session.query(Outgoing).options(joinedload(Outgoing.products),
                                                joinedload(Outgoing.binlocation),
                                                joinedload(Outgoing.projects)).all()
        if len(records) == 0:
            session.close()
            return

        children = self.outg_view.get_children()
        self.outg_view.delete(*children)
        counter = 1
        for record in records:
            if counter % 2 == 0:
                self.outg_view.insert('', tk.END, str(record.id), text=str(record.id), tags='odd')
            else:
                self.outg_view.insert('', tk.END, str(record.id), text=str(record.id), tags='even')
            self.outg_view.set(str(record.id), 'date', datetime.strftime(record.out_date, '%d/%m/%Y'))
            self.outg_view.set(str(record.id), 'code', record.products.code)
            self.outg_view.set(str(record.id), 'name', record.products.name)
            self.outg_view.set(str(record.id), 'unit', record.products.units.code)
            self.outg_view.set(str(record.id), 'price', f'{record.products.price:,.2f}')
            self.outg_view.set(str(record.id), 'quantity', f'{record.quantity}')
            self.outg_view.set(str(record.id), 'bin', record.binlocation.code)
            self.outg_view.set(str(record.id), 'remarks', record.remarks)
            counter+=1
        session.close()

    def save_record(self):
        out_date = datetime.strptime(self.date_entry.get(), '%d/%m/%Y')
        code = self.code_entry.get()
        name = self.name_entry.get()
        idx = self.bin_listbox.curselection()[0]
        binloc = self.bin_listbox.get(idx).split(' ==> ')[0]
        quantity = float(self.qty_entry.get()) * -1
        remarks = self.rema_entry.get()
        proj_name = self.proj_var.get()
        if (name == '') or (quantity == '') or (code == ''):
            mb.showwarning('Incomplete Data', 'Sorry missing data, \n record cannot be save.')
            self.code_entry.focus_set()
            return
        session = DBSession()
        if self.record_id == None:
            prod_record = session.query(Products).filter(Products.code == code).first()
            bin_record = session.query(BinLocation).filter(BinLocation.code == binloc).first()
            proj_record = session.query(Projects).filter(Projects.name == proj_name).first()
            new_record = Outgoing(out_date=out_date, projects=proj_record,
                                products=prod_record, binlocation=bin_record,
                                name=name, quantity=quantity, remarks=remarks)
            session.add(new_record)
        else:
            record = session.query(Outgoing).filter(Outgoing.id == self.record_id).first()
            prod_record = session.query(Products).filter(Products.code == code).first()
            bin_record = session.query(BinLocation).filter(BinLocation.code == binloc).first()
            proj_record = session.query(Projects).filter(Projects.name == proj_name).first()
            record.out_date = out_date
            record.projects = proj_record
            record.products = prod_record
            record.binlocation = bin_record
            record.name = name
            record.quantity = quantity
            record.remarks = remarks
            self.record_id = None
        session.commit()
        session.close()
        self.code_entry.delete('0', tk.END)
        self.bin_listbox.delete('0', tk.END)
        self.name_entry.delete('0', tk.END)
        self.qty_entry.delete('0', tk.END)
        self.rema_entry.delete('0', tk.END)
        self.update_view()
        self.code_entry.focus_set()

    def edit_record(self):
        select_unit = self.outg_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        self.record_id = record_id
        session = DBSession()
        record = session.query(Outgoing).filter(Outgoing.id == record_id).first()
        self.code_entry.delete('0', tk.END)
        self.bin_listbox.delete('0', tk.END)
        self.name_entry.delete('0', tk.END)
        self.date_entry.delete('0', tk.END)
        self.unit_entry.delete('0', tk.END)
        self.qty_entry.delete('0', tk.END)
        self.rema_entry.delete('0', tk.END)

        out_date = datetime.strftime(record.out_date, '%d/%m/%Y')
        project = record.projects.name
        code = record.products.code
        unit = record.products.units.code
        name = record.name
        location = record.binlocation.code
        quantity = str(abs(record.quantity))
        remarks = record.remarks

        self.date_entry.insert(tk.END, out_date)
        self.proj_var.set(project)
        self.code_entry.insert(tk.END, code)
        self.name_entry.insert(tk.END, name)
        self.bin_listbox.insert(tk.END, location+' ==> '+quantity)
        self.bin_listbox.select_set(0)
        self.unit_entry.insert(tk.END, unit)
        self.qty_entry.insert(tk.END, quantity)
        self.rema_entry.insert(tk.END, remarks)

        session.close()
        self.code_entry.focus_set()

    def delete_record(self):
        select_unit = self.outg_view.focus()
        if select_unit == '':
            mb.showwarning('No Record', 'Sorry no record selected.\n Please try again.')
            self.code_entry.focus_set()
            return
        record_id = int(select_unit)
        session = DBSession()
        record = session.query(Outgoing).filter(Outgoing.id == record_id).first()
        answer = mb.askyesno('Delete Record?', 'Are you sure you want to delete?')
        if answer:
            session.delete(record)
            session.commit()
        session.close()
        self.update_view()
        self.code_entry.focus_set()

    def change_date(self):
        date_today = datetime.today()
        tp = tk.Toplevel(self)
        win = CalendarWidget(date_today.year, date_today.month, tp)
        win.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.wait_window(tp)
        if win.date is not None:
            self.date_entry.delete('0', tk.END)
            self.date_entry.insert(tk.END, win.date)
            # self.update_view()

    def close_app(self):
        self.master.destroy()
# End of OutgoingWindow class

# Start of AboutWindow class
class AboutWindow(ttk.Frame):

    def __init__(self, master=None, **kws):
        ttk.Frame.__init__(self, master, **kws)
        self.master.title("About")
        self.master.protocol("WM_DELETE_WINDOW", self.close)
        self.img_list = image_list()
        self.img72_list = image_list(size=(72, 72))
        if os.name == 'nt':
            self.master.iconbitmap('inventory.ico')
        self.setup_ui()
        self.master.grab_set()

    def setup_ui(self):
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X)
        mid_frame = tk.Frame(self)
        mid_frame.pack(fill=tk.X)
        bot_frame = tk.LabelFrame(self, text="MIT License", labelanchor=tk.N)
        bot_frame.pack(expand=True, fill=tk.BOTH)

        logo_lbl = tk.Label(top_frame, image=self.img72_list['inventory'])
        logo_lbl.pack(side=tk.LEFT)

        text = " ".join(["Inventory Management", __version__])

        app_name_lbl = tk.Label(top_frame, text=text,
                                font="Times 11 bold", fg='#611161')
        app_name_lbl.pack(side=tk.LEFT)

        author_lbl = tk.Label(mid_frame, text="Author:")
        author_lbl.grid(row=0, column=0, sticky=tk.W)

        author_name_lbl = tk.Label(mid_frame, text=__author__)
        author_name_lbl.grid(row=0, column=1, sticky=tk.W)

        web_lbl = tk.Label(mid_frame, text="Home Page:")
        web_lbl.grid(row=1, column=0, sticky=tk.W)

        web_name_lbl = tk.Label(mid_frame, text=__web__, fg="blue")
        web_name_lbl.grid(row=1, column=1, sticky=tk.W)

        icons8_lbl = tk.Label(mid_frame, text="Free Icons:")
        icons8_lbl.grid(row=2, column=0, sticky=tk.W)

        icons8_name_lbl = tk.Label(mid_frame, text="https://icons8.com", fg='blue')
        icons8_name_lbl.grid(row=2, column=1, sticky=tk.W)

        self.sc_text = ScrolledText(bot_frame, bd=1)
        self.sc_text.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        with open("LICENSE.txt", 'r') as lic_file:
            data = lic_file.read()

        self.sc_text.insert('1.0', data)
        self.sc_text.config(state="disabled")

        self.okay_btn = ttk.Button(self, text="Okay", command=self.close,
                                   image=self.img_list['okay'], compound=tk.LEFT)
        self.okay_btn.pack()
        self.okay_btn.focus_set()

    def close(self):
        self.master.destroy()
# End of AboutWindow class

# Start of PDF class
class PDF(FPDF):
    def header(self):
        self.set_font('Times', 'B', 20)
        self.cell(0, 10, 'Al Hamra Construction Co. LLC', 0, 1, 'C')
        self.set_font('Times', 'I', 17)
        self.cell(0, 20, 'Current Stock', 0, 1, 'C')
        # Start of table header
        self.set_fill_color(192, 131, 20)
        self.set_text_color(255, 255, 255)
        self.cell(20, 10, 'Sl. No.', 1, 0, 'C', True)
        self.cell(35, 10, 'Item Code', 1, 0, 'C', True)
        self.cell(100, 10, 'Description', 1, 0, 'C', True)
        self.cell(30, 10, 'Unit', 1, 0, 'C', True)
        self.cell(30, 10, 'Price', 1, 0, 'C', True)
        self.cell(30, 10, 'Quantity', 1, 0, 'C', True)
        self.cell(0, 10, 'Amount', 1, 1, 'C', True)
        self.set_font('Times', '', 12)
        self.set_text_color(0, 0, 0)
        # End of table header


    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 9)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + ' of {nb}', 0, 0, 'C')
# End of PDF class

def main():
    root = tk.Tk()
    win = MainWindow(root)
    win.pack(expand=True, fill=tk.BOTH, ipadx=5, ipady=5)
    win.update_view()
    root.mainloop()

if __name__ == '__main__':
    sys.exit(main())
