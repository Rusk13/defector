import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from settings import *

class Panel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color=DARK_GREY)
        self.pack(fill='x', pady=4, ipady = 8)
    
class SliderPanel(Panel):
    def __init__(self, parent, text, exposure_time, min_val, max_val, steps):
        super().__init__(parent=parent)

        #layout
        self.rowconfigure((0,1), weight=1)
        self.columnconfigure((0,1), weight=1)

        ctk.CTkLabel(self, text=  text).grid(column = 0, row = 0, sticky = 'w', padx = 5)
        ctk.CTkLabel(self, textvariable = exposure_time).grid(column = 0, row = 0, sticky = 'e', padx = 5)
        ctk.CTkSlider(
            self, 
            fg_color=SLIDER_BG, 
            variable=exposure_time,
            from_=min_val,
            to=max_val,
            number_of_steps = max_val/steps).grid(row = 1, column = 0, columnspan = 2, sticky = 'ew', padx = 5, pady = 5)

class SwitchPanel(Panel):
    def __init__(self, parent, text, exposure_time):
        super().__init__(parent=parent)

        #layout
        self.rowconfigure((0,1), weight=1)
        self.columnconfigure((0,1), weight=1)

        ctk.CTkLabel(self, text =  text).grid(column = 0, row = 0, sticky = 'w', padx = 5)
        ctk.CTkSwitch(
            self,
            text='',
            fg_color=SLIDER_BG,
            variable=exposure_time).grid(column = 1, row = 0, sticky = 'e')

class ButtonPanel(Panel):
    def __init__(self, parent, text, btn_func):
        super().__init__(parent=parent)

        #layout
        self.rowconfigure((0), weight=1)
        self.columnconfigure((0), weight=1)

        # ctk.CTkLabel(self, text =  text).grid(column = 0, row = 0, sticky = 'w', padx = 5)
        ctk.CTkButton(
            self,
            text=text,
            command=btn_func).grid(column = 0, row = 0, sticky = 'news')

class ComboboxPanel(Panel):
    def __init__(self, parent, text, pcb_list, selected):
        super().__init__(parent=parent)

        #layout
        self.rowconfigure((0,1), weight=1)
        self.columnconfigure((0,1), weight=1)

        ctk.CTkLabel(self, text =  text).grid(column = 0, row = 0, columnspan= 2, sticky = 'news', padx = 5)
        self.combo = ttk.Combobox(
            self,
            state='readonly',
            values = pcb_list,
            textvariable=selected,
            background = BACKGROUND_COLOR)
        self.combo.grid(column = 0, row = 1, columnspan= 2, sticky = 'news')
        # ctk.CTkButton(self, text='Обновить файл', )
class LabelPanel(Panel):
    def __init__(self, parent, pcb_correct):
        super().__init__(parent=parent)
        self.rowconfigure((0), weight=1)
        self.columnconfigure((0), weight=1)
        print(pcb_correct)
        # ctk.CTkLabel(self, text =  text).grid(column = 0, row = 0, sticky = 'w', padx = 5)
        if pcb_correct.get():
            color = 'green'
            text = 'OK'
        else:
            color = 'red'
            text = 'NOT OK'

        ctk.CTkLabel(
            self,
            text=text,
            bg_color=color).grid(column = 0, row = 0, sticky = 'ew')