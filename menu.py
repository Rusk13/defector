import customtkinter as ctk
from panels import *

class Menu(ctk.CTkTabview):
    def __init__(self, parent, exposure_time, red, green, blue, mask_on,pcb_list, selected_model):
        super().__init__(master=parent)
        self.grid(row = 0, column = 0, sticky = 'news', pady = 10, padx = 10)

        self.add('Настройки')
        # self.add('Цвет')
        SettingsFrame(self.tab('Настройки'), exposure_time, red, green, blue, mask_on,pcb_list, selected_model)
        # ColorFrame(self.tab('Цвет'))

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, exposure_time, red, green, blue, mask_on, pcb_list, selected_model):
        super().__init__(master=parent)
        self.pack(expand = True, fill = 'both')
        ComboboxPanel(self, 'Платы', pcb_list, selected_model)
        SliderPanel(self, 'Время экспозиции', exposure_time, 0, 40000, 500)
        SliderPanel(self, 'Red', red, 0, 400, 10)
        SliderPanel(self, 'Green', green, 0, 400, 10)
        SliderPanel(self, 'Blue', blue, 0, 400, 10)
        SwitchPanel(self, 'Вид маски', mask_on)
class ColorFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent)
        self.pack(expand = True, fill = 'both')
