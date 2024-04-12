import customtkinter as ctk
import tkinter as tk
from image_widgtes import *
from PIL import Image, ImageTk
from menu import Menu
from harvesters.core import Harvester
from harvesters.core import DeviceInfo
from harvesters.core import Component2DImage
from harvesters.util.pfnc import mono_location_formats
from PIL import Image 
import numpy as np
import cv2
import statistics
import yaml
class App(ctk.CTk):
    def __init__(self):
        # setup
        super().__init__()
        ctk.set_appearance_mode('dark')
        self.geometry('1000x700')
        self.iconbitmap('favicon.ico')
        self.title('Defect detector')
        self.minsize(800,700)
        with open('pcb.yml', 'r') as file:
            self.pcb_list_file = yaml.safe_load(file)
        self.init_parameters()
        # layout
        self.rowconfigure(0, weight=12)
        self.rowconfigure(1, weight=1)

        self.columnconfigure(0, weight=2, uniform='a')
        self.columnconfigure(1, weight=6, uniform='a')
        self.image_ratio = None
        self.menu = Menu(self, self.exposure_time, self.red_gain, self.green_gain, self.blue_gain, self.mask_on, self.pcb_list, self.selected_model, self.diff_perc, self.gain, self.saturation, self.contrast, self.wb_func, self.pcb_correct, self.update_pcb_file, self.threshold_value)

        self.correct_label = ctk.CTkLabel(
            self,
            text='NOT OK',
            bg_color='red',
            corner_radius=50)
        self.correct_label.grid(row=1, column = 0, sticky='news', padx=10, pady=10)
        # widgtes
        self.image_import = ImageImport(self, self.import_image, self.pcb_list_file[self.selected_model.get()])
        self.image_output = ImageOutput(self, self.resize_image)
        self.image_output.bind('<Configure>', self.resize_image)
        self.canvas_width = self.image_output.winfo_reqwidth()
        self.canvas_height = self.image_output.winfo_reqheight()
        
        print(self.image_import.camera_type.get())
        # run
        self.mainloop()

    def init_parameters(self):

        self.pcb_correct = ctk.BooleanVar(value=False)
        self.exposure_time = ctk.IntVar(value=EXPOSURETIME_DEFAULT)
        self.red_gain = ctk.IntVar(value=RED_DEFAULT)
        self.green_gain = ctk.IntVar(value=GREEN_DEFAULT)
        self.blue_gain = ctk.IntVar(value=BLUE_DEFAULT)
        self.gain = ctk.IntVar(value=GAIN_DEFAULT)
        self.saturation = ctk.IntVar(value=SATURATION_DEFAULT)
        self.contrast = ctk.IntVar(value=CONTRAST_DEFAULT)
        self.mask_on = ctk.BooleanVar(value=False)
        self.threshold_value = ctk.IntVar(value=250)
        self.pcb_list = []
        for pcb in self.pcb_list_file:
            self.pcb_list.append(pcb)
        self.selected_model = tk.StringVar(value=self.pcb_list[0])
        self.diff_perc = ctk.IntVar(value=10)
        self.selected_model.trace_add('write', self.change_model)
        self.exposure_time.trace_add('write', self.manipulate_camera)
        self.diff_perc.trace_add('write', self.change_percantage)
        self.red_gain.trace_add('write', self.manipulate_camera)
        self.green_gain.trace_add('write', self.manipulate_camera)
        self.blue_gain.trace_add('write', self.manipulate_camera)
        self.gain.trace_add('write', self.manipulate_camera)
        self.saturation.trace_add('write', self.manipulate_camera)
        self.contrast.trace_add('write', self.manipulate_camera)
        self.mask_on.trace_add('write', self.change_view)
        self.threshold_value.trace_add('write', self.change_threshold)
        self.pcb_correct.trace_add('write', self.change_correct_label)
    def wb_func(self):
        self.image_import.ia.remote_device.node_map.WBOnce.execute()
    def update_pcb_file(self):
        with open('pcb.yml', 'r') as file:
            self.pcb_list_file = yaml.safe_load(file)
        self.selected_model.set(self.pcb_list[0])
        self.pcb_list = []
        for pcb in self.pcb_list_file:
            self.pcb_list.append(pcb)
        self.menu.settings_frame.pcb_box.combo['values']=self.pcb_list
        # self.menu.settings_frame.pcb_box.pack_forget()
        # self.menu.settings_frame.pcb_box.pack()
    def manipulate_camera(self, *args):
        self.image_import.ia.remote_device.node_map.ExposureTime.value = int(self.exposure_time.get())
        self.image_import.ia.remote_device.node_map.RGain.value = int(self.red_gain.get())
        self.image_import.ia.remote_device.node_map.GGain.value = int(self.green_gain.get())
        self.image_import.ia.remote_device.node_map.BGain.value = int(self.blue_gain.get())
        self.image_import.ia.remote_device.node_map.Gain.value = int(self.gain.get())
        self.image_import.ia.remote_device.node_map.Saturation.value = int(self.saturation.get())
        self.image_import.ia.remote_device.node_map.Contrast.value = int(self.contrast.get())
    def change_model(self, *args):
        print('model: ', self.selected_model.get())
        if self.selected_model.get() != '':
            self.image_import.led_points = self.pcb_list_file[self.selected_model.get()]
    def change_view(self, *args):
        self.image_import.mask_on = self.mask_on.get()
    def change_percantage(self, *args):
        self.image_import.threshold_percentage = self.diff_perc.get()
    def change_threshold(self, *args):
        self.image_import.threshold_value = self.threshold_value.get()
    def change_correct_label(self, *args):
        if self.pcb_correct.get():
            self.correct_label.configure(bg_color="green")
            self.correct_label.configure(text="OK")
        else:
            self.correct_label.configure(bg_color="red")
            self.correct_label.configure(text="NOT OK")

    def import_image(self, path, pcb_correct):
        self.image = Image.fromarray(path)
        self.image_ratio = self.image.size[0] / self.image.size[1]
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.image_import.grid_forget()
        self.image_output.delete('all')
        self.pcb_correct.set(pcb_correct)
        self.draw_image()
        
    def resize_image(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height
    def draw_image(self):
        # current canvas ration
        # print(self.image_ratio)
        if self.image_ratio == None:
            return
        canvas_ratio = int(self.canvas_width) / int(self.canvas_height)
        # resize
        if canvas_ratio > self.image_ratio:
            image_height = int(self.canvas_height)
            image_width = int(image_height * self.image_ratio)
        else:
            image_width = int(self.canvas_width)
            image_height = int(image_width / self.image_ratio)
            # print(self.canvas_width, image_height)

        # place image
        self.image_output.delete('all')
        resized_image = self.image.resize((image_width, image_height))
        self.image_tk = ImageTk.PhotoImage(resized_image)
        self.image_output.create_image(int(self.canvas_width) / 2, int(self.canvas_height) / 2, image = self.image_tk)
App()