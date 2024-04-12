import customtkinter as ctk
from panels import *

class Menu(ctk.CTkTabview):
    def __init__(self, parent, exposure_time, red, green, blue, mask_on,pcb_list, selected_model, diff_perc, gain, saturation, contrast, wb_func, pcb_correct, update_pcb_file, threshold_value):
        super().__init__(master=parent)
        self.grid(row = 0, column = 0, sticky = 'news', pady = 10, padx = 10)

        self.add('Управление')
        self.add('Настройки камеры')
        self.settings_frame = SettingsFrame(self.tab('Управление'), exposure_time, diff_perc, mask_on,pcb_list, selected_model, pcb_correct,update_pcb_file, threshold_value)
        ColorFrame(self.tab('Настройки камеры'), red, green, blue, gain, saturation, contrast, wb_func)

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, exposure_time, diff_perc, mask_on, pcb_list, selected_model, pcb_correct, update_pcb_file, threshold_value):
        super().__init__(master=parent)
        self.pack(expand = True, fill = 'both')
        self.pcb_box = ComboboxPanel(self, 'Платы', pcb_list, selected_model)
        ButtonPanel(self, 'Обновить файл', update_pcb_file)
        SliderPanel(self, 'Время экспозиции', exposure_time, 0, 40000, 500)
        SliderPanel(self, 'Процент отклонения', diff_perc, 0, 100, 5)
        SliderPanel(self, 'Threshold value', threshold_value, 0, 254, 5)

        SwitchPanel(self, 'Вид маски', mask_on)
        # LabelPanel(self, pcb_correct)
class ColorFrame(ctk.CTkFrame):
    def __init__(self, parent, red, green, blue, gain, saturation, contrast, wb_func):
        super().__init__(master=parent)
        self.pack(expand = True, fill = 'both')
        ButtonPanel(self, 'Баланс белого', wb_func)
        SliderPanel(self, 'Red', red, 0, 400, 10)
        SliderPanel(self, 'Green', green, 0, 400, 10)
        SliderPanel(self, 'Blue', blue, 0, 400, 10)
        SliderPanel(self, 'Яркость', gain, 1, 16, 1)
        SliderPanel(self, 'Насыщеность', saturation, 0, 200, 10)
        SliderPanel(self, 'Контраст', contrast, 0, 200, 10)

