from typing import Any
import customtkinter as ctk
from tkinter import filedialog, Canvas
from settings import *
from harvesters.core import Harvester
import cv2
import numpy as np
import statistics
import re


class ImageImport(ctk.CTkFrame):
    def __init__(self, parent, import_func, init_leds):
        super().__init__(master=parent)
        self.grid(column = 0,  row = 0, rowspan = 2, sticky = 'news')
        self.import_func = import_func
        self.h = Harvester()
        self.mask_on = False
        self.threshold_value = 250
        self.threshold_percentage = 10
        self.led_points = init_leds
        self.h.add_file(CTI_FILE)
        self.h.update()
        self.camera_list = []
        self.unique_cameras = {}
        self.pcb_led_correct = False
        print(self.h.device_info_list)
        # Get a list of camera indices, names, and serial numbers
        camera_info_list = [(i, camera_info.model, camera_info.serial_number) for i, camera_info in
                            enumerate(self.h.device_info_list)]

        # Iterate through the camera_info_list to add unique cameras to the dictionary
        for index, model, serial_number in camera_info_list:
            unique_camera_identifier = f"{model} ({serial_number})"
            self.unique_cameras[unique_camera_identifier] = index
        print(self.unique_cameras)
        # Extract the unique camera info list from the dictionary
        self.unique_camera_info_list = [identifier for identifier in self.unique_cameras.keys()]
        self.camera_type = ctk.StringVar(value='Gige')
        self.camera_type.trace_add('write', self.change_camera_type)
        self.camera_gige = ctk.CTkRadioButton(self, text='Gige Camera', value='Gige', variable=self.camera_type)
        self.camera_usb = ctk.CTkRadioButton(self, text='Usb Camera', value='Usb', variable=self.camera_type)
        self.camera_gige.place(relx=0.05, rely=0.40)
        self.camera_usb.place(relx=0.55, rely=0.40)
        self.selected_camera = ctk.StringVar(value=self.unique_camera_info_list[0])
        self.cameras = ctk.CTkComboBox(self, values=self.unique_camera_info_list, variable=self.selected_camera)
        self.cameras.place(relx=0.5, rely=0.5, relwidth = 0.9, anchor = 'center')
        ctk.CTkButton(self, text = 'Подключиться', command=self.open_dialog).place(relx=0.5, rely=0.55, relwidth = 0.9, anchor = 'center')
        # Populate the camera selection dropdown with unique camera models

    def change_camera_type(self, *args):
        if self.camera_type.get() == 'Gige':
            self.cameras.configure(values = self.unique_camera_info_list)
        else:
            self.cameras.configure(values = ['USB CAMERA'])
            self.selected_camera.set('0')
        
    def open_dialog(self):
        if self.camera_type.get() == 'Gige':
            camera_str = self.selected_camera.get()
            res = re.findall(r'\(([A-Za-z0-9_]+)\)', camera_str)
            self.ia = self.h.create({"serial_number":res[0]})
            # print(dir(self.ia.remote_device.node_map))
            # print((self.ia.remote_device.node_map._get_nodes))
            self.ia.remote_device.node_map.RGain.value = 260
            self.ia.remote_device.node_map.GGain.value = 200
            self.ia.remote_device.node_map.BGain.value = 300
            self.ia.remote_device.node_map.Gain.value = 8
            self.ia.remote_device.node_map.ExposureTime.value = 20000

            self.ia.remote_device.node_map.Saturation.value = 100
            self.ia.remote_device.node_map.Contrast.value = 100
            self.ia.remote_device.node_map.Height.value = 1080
            self.ia.remote_device.node_map.Width.value = 1920
            
            # ia.remote_device.node_map.PixelFormat.value = 'BayerGB8'
            # print(self.ia.remote_device.node_map.Gain.value)

            # print(dir(self.ia.remote_device.node_map))
            self.ia.start()
            # while True:
            self.update_frame()
        else:
            self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            # while True:
            self.update_frame()
    def getMedianAreaOfContours(self, contours):
        if len(contours) == 0:
            return 0
        sumOfContours = 0
        areas = []
        for i in contours:
            area = cv2.contourArea(i)
            areas.append(area)
        return statistics.median(areas)
    def drawLedContoursAndGetCenters(self, contours,img):
        contoursCenters = []
        ci = 0
        median = self.getMedianAreaOfContours(contours)
        # print(median)
        for i in contours:
            area = cv2.contourArea(i)
            if area < median and abs(median - area) > (median / 100 * self.threshold_percentage):
                continue
            M = cv2.moments(i)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                cv2.drawContours(img, [i], -1, (0, 255, 0), 2)
                cv2.circle(img, (cx, cy), 7, (0, 0, 255), -1)
                cv2.putText(img, str(area), (cx - 20, cy - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                contoursCenters.append((cx,cy))
                # ci += 1
                # if abs(prevCx - cx) < 800 and abs(prevCy - cy) < 20:
                #     cv2.line(img, (prevCx, prevCy), (cx, cy), (0, 255, 0), thickness=3, lineType=8)

                ci += 1
                # cv2.line(img, (prevCx, prevCy), (cx, cy), (0, 255, 0), thickness=3, lineType=8)

                # prevCx = cx
                # prevCy = cy
                # print(f"x: {cx} y: {cy}")
        return contoursCenters

    def update_frame(self):
        if self.camera_type.get() == 'Gige':
            with self.ia.fetch(timeout=np.float32(1)) as buffer:
                component = buffer.payload.components[0]
                _2d = component.data.reshape(component.height, component.width, int(component.num_components_per_pixel))
                img = _2d
                img = cv2.cvtColor(img, cv2.COLOR_BayerGR2RGB)
                img = cv2.resize(img,(1280,720))
                grey_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                # blur = cv2.GaussianBlur(grey_img, (11, 11), 
                #             0)
                ret,thresh1 = cv2.threshold(grey_img,self.threshold_value,255,cv2.THRESH_BINARY)
                thresh1 = cv2.erode(thresh1, None, iterations=2)
                thresh1 = cv2.dilate(thresh1, None, iterations=4)
                contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                # (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(blur)
                # cv2.circle(img, maxLoc, 5, (255, 0, 0), 2)
                contoursCenters = self.drawLedContoursAndGetCenters(contours, img)
                if self.led_points == len(contoursCenters):
                    self.pcb_led_correct = True
                else:
                    self.pcb_led_correct = False
                if self.pcb_led_correct:
                    cv2.putText(img, str(self.pcb_led_correct), (0, 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.putText(img, str(len(contoursCenters)), (60, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                else:
                    cv2.putText(img, str(self.pcb_led_correct), (0, 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    cv2.putText(img, str(len(contoursCenters)), (60, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(img, str(self.led_points), (100, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(img, str(self.ia.remote_device.node_map.ExposureTime.value), (0, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                if self.mask_on:
                    self.import_func(thresh1, self.pcb_led_correct)
                else:
                    self.import_func(img, self.pcb_led_correct)
        else:
            cnt, img = self.cam.read()
            # component = buffer.payload.components[0]
            # _2d = component.data.reshape(component.height, component.width, int(component.num_components_per_pixel))
            # img = _2d
            # img = cv2.cvtColor(img, cv2.COLOR_BayerGR2RGB)
            # img = cv2.resize(img,(1280,720))
            grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # blur = cv2.GaussianBlur(grey_img, (11, 11), 
            #             0)
            ret,thresh1 = cv2.threshold(grey_img,self.threshold_value,255,cv2.THRESH_BINARY)
            thresh1 = cv2.erode(thresh1, None, iterations=2)
            thresh1 = cv2.dilate(thresh1, None, iterations=4)
            contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            # (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(blur)
            # cv2.circle(img, maxLoc, 5, (255, 0, 0), 2)
            contoursCenters = self.drawLedContoursAndGetCenters(contours, img)
            if self.led_points == len(contoursCenters):
                self.pcb_led_correct = True
            else:
                self.pcb_led_correct = False
            if self.pcb_led_correct:
                cv2.putText(img, str(self.pcb_led_correct), (0, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(img, str(len(contoursCenters)), (60, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            else:
                cv2.putText(img, str(self.pcb_led_correct), (0, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(img, str(len(contoursCenters)), (60, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(img, str(self.led_points), (100, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            if self.mask_on:
                self.import_func(thresh1, self.pcb_led_correct)
            else:
                self.import_func(img, self.pcb_led_correct)
        self.after(10, self.update_frame)
class ImageOutput(Canvas):
    def __init__(self, parent, resize_image):
        super().__init__(master=parent, background=BACKGROUND_COLOR, bd = 0, highlightthickness=0, relief='ridge')
        print(self)
        self.grid(row=0, column=1, rowspan=2, sticky='news', padx= 10 , pady = 10)
        self.bind('<Configure>', resize_image)