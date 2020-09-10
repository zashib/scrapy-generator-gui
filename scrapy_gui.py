# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
import scrapy_gen
import os
import threading

SETTINGS = ['default settings', 'proxy', 'images(default)', 'images(named)', 'headers', 'csv', 'json']


def to_dict(**kwargs):
    """Create a dictionary from keyword arguments"""
    dict = locals()
    return dict['kwargs']


class GenGui(tk.Tk):
    items_list = []

    def __init__(self, width=15, text='', onvalue=1, offvalue=0):
        super().__init__()

        self.ch_btn = to_dict(onvalue=onvalue, offvalue=offvalue, width=width)
        self.dest_dir = 'test_test'
        self.start_url = 'https://test.ru'
        self.settings_list = []
        self.all_variables = []
        self.all_entry = []
        self.status_list = []
        self.row_count = 0
        self.column_count = 0
        self.count = 1

        self.title('Scrapy Generator')

        # Add frames
        self.head_frame = ttk.Frame(self)
        self.head_frame.grid(row=0, column=0)
        self.check_frame = ttk.Frame(self)
        self.check_frame.grid(row=1, column=0)
        self.space_frame = ttk.Frame(self, height=10)
        self.space_frame.grid(row=2, column=0)
        self.add_frame = ttk.Frame(self)
        self.add_frame.grid(row=3, column=0)
        self.gen_frame = ttk.Frame(self)
        self.gen_frame.grid(row=4, column=0)

        # Add project name and url
        self.dest_dir = tk.StringVar()
        proj_name = ttk.Label(self.head_frame, text='Project name', width=12)
        proj_name.grid(row=0, column=0)
        ent_proj = tk.Entry(self.head_frame, width=20, textvariable=self.dest_dir)
        ent_proj.grid(row=0, column=1)

        self.start_url = tk.StringVar()
        proj_name = ttk.Label(self.head_frame, text='Start url', width=8)
        proj_name.grid(row=0, column=2)
        ent_proj = tk.Entry(self.head_frame, width=30, textvariable=self.start_url)
        ent_proj.grid(row=0, column=3)

        # Add items with path
        self.gen_chk_btn()
        search_btn = ttk.Button(self.add_frame, text='Add Item', width=8, command=self.add_entry).grid(row=0, column=0)

        item_name = ttk.Label(self.add_frame, text='Name', width=10)
        item_name.grid(row=0, column=1)

        item_name = ttk.Label(self.add_frame, text='Path', width=55)
        item_name.grid(row=0, column=2)

        # Add process buttons
        gen_btn = ttk.Button(self.gen_frame, text='Generate', width=8, command=self.generate).grid(row=0, column=0)
        gen_btn = ttk.Button(self.gen_frame, text='Run shell', width=8, command=self.run_shell).grid(row=0, column=1)

    def check_var(self):
        """Check variable values"""
        temp_vars = []
        for index, var in enumerate(self.all_variables):
            if var.get() != self.status_list[index]:
                if not SETTINGS[index] in self.settings_list:
                    self.settings_list.append(SETTINGS[index])
                else:
                    self.settings_list.remove(SETTINGS[index])
                self.status_list[index] = var.get()

    def gen_chk_btn(self):
        """Create Checkbutton according to SETTINGS"""
        row = 0
        column = 0
        for index, name in enumerate(SETTINGS):
            if column % 3 == 0:
                row += 1
                column = 0
            var = tk.BooleanVar()
            self.all_variables.append(var)
            self.status_list.append(var.get())
            ttk.Checkbutton(self.check_frame, text=name, variable=var, **self.ch_btn, command=self.check_var).grid(
                row=row, column=column)
            column += 1

    def add_entry(self):
        """Add Entry"""
        if self.row_count % 30 == 0 and self.row_count != 0:
            self.column_count += 3
            self.row_count = 0

        ent = ttk.Label(self.add_frame, text='Item' + str(self.count), width=8)
        ent.grid(row=self.row_count + 1, column=self.column_count)

        # Add entry in second row
        var1 = tk.StringVar()
        var2 = tk.StringVar()
        ent = tk.Entry(self.add_frame, width=10, textvariable=var1)
        ent.grid(row=self.row_count + 1, column=self.column_count + 1)

        ent = tk.Entry(self.add_frame, width=55, textvariable=var2)
        ent.grid(row=self.row_count + 1, column=self.column_count + 2)
        self.all_entry.append((var1, var2))
        self.row_count += 1
        self.count += 1

    def generate(self):
        """Generate python code"""
        items = []
        items_path = []

        for item_name, item_path in self.all_entry:
            items.append(item_name.get())
            items_path.append(item_path.get())

        scrapy_gen.ScrapyGen(items=items, items_path=items_path, settings_list=self.settings_list,
                             dest_dir=self.dest_dir.get(), start_url=self.start_url.get())

    def run_shell(self):
        """Run scrapy shell"""
        my_thread = threading.Thread(target=os.system, args=('scrapy shell "%s"' % self.start_url.get(),))
        my_thread.start()


if __name__ == '__main__':
    ui = GenGui()
    ui.mainloop()
