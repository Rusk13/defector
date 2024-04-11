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
        self.geometry('1000x600')
        self.iconbitmap('favicon.ico')
        self.title('Defect detector')
        self.minsize(800,500)
        with open('pcb.yml', 'r') as file:
            self.pcb_list_file = yaml.safe_load(file)
        self.init_parameters()
        # layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=2, uniform='a')
        self.columnconfigure(1, weight=6, uniform='a')
        self.image_ratio = None
        self.menu = Menu(self, self.exposure_time, self.red_gain, self.green_gain, self.blue_gain, self.mask_on, self.pcb_list, self.selected_model)


        # widgtes
        # ctk.CTkButton(self, text = 'open image', command=self.open_dialog).grid(row=0, column=0)
        self.image_import = ImageImport(self, self.import_image, self.pcb_list_file[self.selected_model.get()])
        self.image_output = ImageOutput(self, self.resize_image)
        self.canvas_width = 800
        self.canvas_height = 600
        # run
        self.mainloop()
    # def open_dialog(self):
    #     self.ia.start()
    #     self.ia.remote_device.node_map.WBOnce.execute()
    #     print('before loop')
    #     # while True:
    #     self.update_frame()

    # def update_frame(self):
    #     with self.ia.fetch(timeout=np.float32(1)) as buffer:
    #         component = buffer.payload.components[0]
    #         _2d = component.data.reshape(component.height, component.width, int(component.num_components_per_pixel))
    #         img = _2d
    #         img = cv2.cvtColor(img, cv2.COLOR_BayerGR2RGB)
    #         img = cv2.resize(img,(1600,900))
    #         self.import_func(img)
    #     self.after(1, self.update_frame)
    def init_parameters(self):

        self.exposure_time = ctk.IntVar(value=EXPOSURETIME_DEFAULT)
        self.red_gain = ctk.IntVar(value=RED_DEFAULT)
        self.green_gain = ctk.IntVar(value=GREEN_DEFAULT)
        self.blue_gain = ctk.IntVar(value=BLUE_DEFAULT)
        self.mask_on = ctk.BooleanVar(value=False)
        self.pcb_list = []
        for pcb in self.pcb_list_file:
            self.pcb_list.append(pcb)
        self.selected_model = tk.StringVar(value=self.pcb_list[0])
        
        self.selected_model.trace_add('write', self.change_model)
        self.exposure_time.trace_add('write', self.manipulate_camera)
        self.red_gain.trace_add('write', self.manipulate_camera)
        self.green_gain.trace_add('write', self.manipulate_camera)
        self.blue_gain.trace_add('write', self.manipulate_camera)
        self.mask_on.trace_add('write', self.change_view)

    def manipulate_camera(self, *args):
        self.image_import.ia.remote_device.node_map.ExposureTime.value = int(self.exposure_time.get())
        self.image_import.ia.remote_device.node_map.RGain.value = int(self.red_gain.get())
        self.image_import.ia.remote_device.node_map.GGain.value = int(self.green_gain.get())
        self.image_import.ia.remote_device.node_map.BGain.value = int(self.blue_gain.get())
    def change_model(self, *args):
        print('model: ', self.selected_model.get())
        if self.selected_model.get() != '':
            self.image_import.led_points = self.pcb_list_file[self.selected_model.get()]
    def change_view(self, *args):
        self.image_import.mask_on = self.mask_on.get()

    # def update_frame(self):
    #     with ImageImport.ia.fetch(timeout=np.float32(1)) as buffer:
    #         component = buffer.payload.components[0]
    #         _2d = component.data.reshape(component.height, component.width, int(component.num_components_per_pixel))
    #         img = _2d
    #         img = cv2.cvtColor(img, cv2.COLOR_BayerGR2RGB)
    #         img = cv2.resize(img,(1600,900))
    #         self.resize_image()
    #     self.after(1, self.update_frame)
    def import_image(self, path):
        self.image = Image.fromarray(path)
        self.image_ratio = self.image.size[0] / self.image.size[1]
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.image_import.grid_forget()
        # if len(self.image_output.find_all()) == 0:
        self.image_output.delete('all')
        self.draw_image()
        # self.image_output.create_image(int(self.image_output['width']) / 2, int(self.image_output['height']) / 2, image = self.image_tk)
        
    def resize_image(self, event):
        # current canvas ration
        # print(self.image_ratio)

        if self.image_ratio == None:
            return
        self.canvas_width = event.width
        self.canvas_height = event.height
        # canvas_ratio = self.canvas_width / self.canvas_height

        # # resize
        # if canvas_ratio > self.image_ratio:
        #     image_height = int(event.height)
        #     image_width = int(image_height * self.image_ratio)
        # else:
        #     image_width = int(event.width)
        #     image_height = int(image_width / self.image_ratio)

        # # place image
        # self.image_output.delete('all')
        # resized_image = self.image.resize((image_width, image_height))
        # self.image_tk = ImageTk.PhotoImage(resized_image)
        # self.image_output.create_image(event.width / 2, event.height / 2, image = self.image_tk)
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