
import os
from pathlib import Path
import sys
import math
import json
from tkinter import dialog
from PIL import Image
from typing import Callable, Literal
import customtkinter as ctk
import pygame
from settings import *

class GraphCalculator:
    def __init__(self, func_file: FileType, send_graph_info_func: Callable[[str, int], None], remove_graph_info_func: Callable[[int], None]) -> None:
        ctk.set_default_color_theme('blue')
        ctk.set_appearance_mode('dark')
        ctk.set_window_scaling(0.8)
        ctk.set_widget_scaling(0.8)
        
        self.root = ctk.CTk()
        
        self.scr_width = 1000
        self.scr_height = 600
        
        self.root.geometry(f'{self.scr_width}x{self.scr_height}')
        self.root.minsize(self.scr_width, self.scr_height)
        
        self.func_file = func_file
        self.send_graph_info_func = send_graph_info_func
        self.remove_graph_info_func = remove_graph_info_func
        
        self.frame_id = 'frame'
        self.menu_bar_frame_id = 'menuframebar'
        self.index_id = 'index'
        self.cursor_id = 'cursor'
        self.keystrokes_id = 'keystrokes'
        self.color_sliders_id = 'colorsliders'
        self.color_entry_id = 'colorentry'
        self.color_button_id = 'colorbutton'
        self.color_entry_repr_id = 'colorer'
        self.color_editor_enables_id = '9102u31932'
        self.toogle_state_button_id = '1ee1e12e'
        
        self.funtion_calcs_info = {}
        
        self.display_color = '#111111'
        self.frame_bar_color = 'black'
        self.cursor_char = '|'
        self.x_id = 'x'
        
        self.all_maths_funcs = []
        for name, probaable_func in [(n, p_f) for n, p_f in math.__dict__.items() if isinstance(p_f, Callable)]:
            try:
                if not isinstance(probaable_func(1), int | float):
                    raise TypeError('Whatever')
                if isinstance(probaable_func(1), bool):
                    raise TypeError('Whatever')
            except TypeError:
                continue
            except ValueError:
                pass
            
            self.all_maths_funcs.append(name)
        self.all_maths_funcs.sort()
        
        self.menubar_bg_frame = ctk.CTkFrame(self.root, height=20, fg_color=self.frame_bar_color, corner_radius=0)
        self.menubar_bg_frame.place(relx=0, rely=0, relwidth=1)
        
        self.frame_menu_bar = ctk.CTkFrame(self.menubar_bg_frame, corner_radius=0, fg_color=self.frame_bar_color, height=20)#, height=ctk.CTkFont()._size * 2.5, orientation='horizontal', scrollbar_button_color=self.frame_bar_color, scrollbar_button_hover_color='#f0f0f0')
        self.frame_menu_bar.pack(side='left', pady=2, fill='x', expand=True)
        ctk.CTkButton(self.menubar_bg_frame, 20, 20, text='+', corner_radius=10, command=self.add_sub_calc).pack(side='right')
        
        self._add_sub_calc('Straight Line Graph', False)
    
    def _set_color(self, color: ColorType, opacity: int, hex_: bool = True):
        if isinstance(color, str):
            if '#' in color:
                color_tuple = [(math.fabs(255 - (col * 255)) / 255) for col in pygame.Color(color).cmy]
            else:
                color_tuple = [i/255 for i in pygame.colordict.THECOLORS[color]]
        elif isinstance(color, tuple | list | pygame.color.Color):
            color_tuple = [i/255 for i in color]
        elif isinstance(color, int):
            color_tuple = [i/255 for i in pygame.Color(color)]
        else:
            raise Exception('Invalid color argument')

        for i in color_tuple[:3]:
            black = i == 0
            if not black:
                break
        
        color = [255 - opacity for _ in color_tuple] if black else [i * opacity for i in color_tuple]
        
        if len(color) >= 4:
            color = color[:3]

        return self._rgb_to_hex(color) if hex_ else color
    
    def _rgb_to_hex(self, rgb):
        rgb = tuple(int(max(0, min(255, component))) for component in rgb)
        hex_color = "#{:02X}{:02X}{:02X}".format(*rgb)
        
        return hex_color
    
    def _is_color(self, color):
        try:
            pygame.colordict.THECOLORS[color]
        except:
            try:
                pygame.Color(color).cmy
            except:
                return False
            return True
        return True
    
    def _make_sub_calc(self, name: str):
        frame = self.funtion_calcs_info[name][self.frame_id]
        index = self.funtion_calcs_info[name][self.index_id]
        
        master_frame1 = ctk.CTkFrame(frame)
        master_frame1.pack(side='top', pady=2, fill='x', expand=True)
        master_frame2 = ctk.CTkFrame(frame)
        master_frame2.pack(side='left', pady=2, fill='both', expand=True)
        master_frame3 = ctk.CTkFrame(frame)
        master_frame3.pack(side='top', pady=2, fill='y', expand=True)
        master_frame4 = ctk.CTkFrame(frame, fg_color='transparent')
        master_frame4.pack(side='bottom', pady=2, fill='both', expand=True)
        
        sub_frame1 = ctk.CTkScrollableFrame(master_frame1, fg_color=self.display_color, height=ctk.CTkFont()._size * 2, orientation='horizontal', scrollbar_button_color=self.display_color, scrollbar_button_hover_color='#f0f0f0')
        sub_frame1.pack(side='left', fill='x', expand=True)
        cancel_buttons_frame = ctk.CTkFrame(master_frame1)
        cancel_buttons_frame.pack(side='right', padx=10, pady=5)
        ctk.CTkButton(cancel_buttons_frame, text='<', width=30, command=lambda: self.backspace_text(name, display_label)).pack()
        ctk.CTkButton(cancel_buttons_frame, text='C', width=30, command=lambda: self.clear_all(name, display_label)).pack()
        
        slider_frame = ctk.CTkFrame(master_frame4, height=32)
        slider_frame.pack(pady=5)
        color_button_and_color_entry_frame = ctk.CTkFrame(master_frame4, height=32)
        color_button_and_color_entry_frame.pack(fill='x', padx=5)
        toogle_state_button = ctk.CTkButton(master_frame4, text='Deactivate Color Editor', text_color='black', hover_color=self._set_color('black', 50), fg_color='white', command=lambda: self._toogle_color_editor_state(name))
        toogle_state_button.pack(side='bottom', fill='x', pady=5)
        
        slider1_frame = ctk.CTkFrame(slider_frame, height=32)
        slider1_frame.pack(pady=5)
        slider2_frame = ctk.CTkFrame(slider_frame, height=32)
        slider2_frame.pack(pady=2)
        slider3_frame = ctk.CTkFrame(slider_frame, height=32)
        slider3_frame.pack(pady=5)
        
        color_sliders = []
        
        def create_color_sliders(frame: ctk.CTkFrame, color_name: str):
            ctk.CTkLabel(frame, text=color_name).pack(side='left', padx=5)
            ctk.CTkLabel(frame, text='0').pack(side='left', padx=5)
            slider = ctk.CTkSlider(frame, from_=0, to=255, command=lambda trash: self._slider_color_update(name))
            slider.pack(side='left')
            ctk.CTkLabel(frame, text='255').pack(side='left', padx=5)
            color_sliders.append(slider)
        
        key_strokes_binding_list = [
            lambda: self.root.bind('a', lambda m: self.move_cursor(name, display_label, -1)),
            lambda: self.root.bind('d', lambda m: self.move_cursor(name, display_label, 1)),
            lambda: self.root.bind('b', lambda m: self.backspace_text(name, display_label)),
            lambda: self.root.bind('(', lambda m: self.update_text(name, display_label, '(')),
            lambda: self.root.bind(')', lambda m: self.update_text(name, display_label, ')')),
            lambda: self.root.bind('e', lambda m: self.move_to_endings(name, display_label, 1)),
            lambda: self.root.bind('h', lambda m: self.move_to_endings(name, display_label, -1)),
            lambda: self.root.bind('c', lambda m: self.clear_all(name, display_label)),
        ]
        
        self.initial_display_label = display_label = ctk.CTkLabel(sub_frame1, fg_color='transparent', text=self.cursor_char, anchor='w', font=ctk.CTkFont(size=20, weight='bold'))
        display_label.pack(side='left', fill='x', expand=True, padx=5)
        
        self.funtion_calcs_info[name].update({self.keystrokes_id: key_strokes_binding_list})
        self.funtion_calcs_info[name].update({self.color_sliders_id: color_sliders})
        
        create_color_sliders(slider1_frame, 'Red')
        create_color_sliders(slider2_frame, 'Green')
        create_color_sliders(slider3_frame, 'Blue')
        
        color_entry = ctk.CTkEntry(color_button_and_color_entry_frame)
        color_entry.pack(side='left', padx=10)
        color_button = ctk.CTkButton(color_button_and_color_entry_frame, text='', width=28, fg_color='red', hover=False)
        color_button.pack(side='right')
        
        self.funtion_calcs_info[name][self.color_editor_enables_id] = True
        self.funtion_calcs_info[name][self.color_entry_id] = color_entry
        self.funtion_calcs_info[name][self.color_button_id] = color_button
        self.funtion_calcs_info[name][self.color_entry_repr_id] = repr(self.root.focus_get())
        self.funtion_calcs_info[name][self.toogle_state_button_id] = toogle_state_button
        
        def update_focus():
            color_entry.focus_force()
            self.funtion_calcs_info[name][self.color_entry_repr_id] = repr(self.root.focus_get())
        
        self.root.after(2000, update_focus)
        
        calculator_column1 = ctk.CTkFrame(master_frame2)
        calculator_column1.pack(pady=2, fill='both', expand=True)
        calculator_column2 = ctk.CTkFrame(master_frame2)
        calculator_column2.pack(pady=2, fill='both', expand=True)
        calculator_column3 = ctk.CTkFrame(master_frame2)
        calculator_column3.pack(pady=2, fill='both', expand=True)
        calculator_column4 = ctk.CTkFrame(master_frame2)
        calculator_column4.pack(pady=2, fill='both', expand=True)
        calculator_column5 = ctk.CTkFrame(master_frame2)
        calculator_column5.pack(pady=2, fill='both', expand=True)
        calculator_column6 = ctk.CTkFrame(master_frame2)
        calculator_column6.pack(pady=2, fill='both', expand=True)
        calculator_column7 = ctk.CTkFrame(master_frame2)
        calculator_column7.pack(pady=2, fill='both', expand=True)

        def update_text_name_func(func_name): return lambda: self.update_text(name, display_label, func_name + '(')
        
        special_operations_frame = ctk.CTkScrollableFrame(master_frame3, width=210)
        special_operations_frame.pack(fill='both', expand=True)
        
        special_operations_sub_frames = [ctk.CTkFrame(special_operations_frame) for _ in range(10)]
        
        for func_name_index, func_name in enumerate(self.all_maths_funcs):
            ctk.CTkButton(special_operations_sub_frames[func_name_index % len(special_operations_sub_frames)], 100, text=func_name, command=update_text_name_func(func_name)).pack(side='left', fill='x', expand=True, padx=10, pady=5)
        
        for frames in special_operations_sub_frames:
            frames.pack(pady=2)
        
        self.make_generic_button(name, display_label, calculator_column1, key_strokes_binding_list, '7')
        self.make_generic_button(name, display_label, calculator_column1, key_strokes_binding_list, '8')
        self.make_generic_button(name, display_label, calculator_column1, key_strokes_binding_list, '9')
        self.make_generic_button(name, display_label, calculator_column1, key_strokes_binding_list, ' + ')
        
        self.make_generic_button(name, display_label, calculator_column2, key_strokes_binding_list, '6')
        self.make_generic_button(name, display_label, calculator_column2, key_strokes_binding_list, '5')
        self.make_generic_button(name, display_label, calculator_column2, key_strokes_binding_list, '4')
        self.make_generic_button(name, display_label, calculator_column2, key_strokes_binding_list, ' - ')
        
        self.make_generic_button(name, display_label, calculator_column3, key_strokes_binding_list, '3')
        self.make_generic_button(name, display_label, calculator_column3, key_strokes_binding_list, '2')
        self.make_generic_button(name, display_label, calculator_column3, key_strokes_binding_list, '1')
        self.make_generic_button(name, display_label, calculator_column3, key_strokes_binding_list, ' * ')
        
        self.make_generic_button(name, display_label, calculator_column4, key_strokes_binding_list, self.x_id)
        self.make_generic_button(name, display_label, calculator_column4, key_strokes_binding_list, '0')
        self.make_generic_button(name, display_label, calculator_column4, key_strokes_binding_list, '.')
        self.make_generic_button(name, display_label, calculator_column4, key_strokes_binding_list, ' / ')
        
        self.make_generic_button(name, display_label, calculator_column5, key_strokes_binding_list, '2', lambda: self.update_text(name, display_label, '`2'), font_size_increase=0.5)
        self.make_generic_button(name, display_label, calculator_column5, key_strokes_binding_list, '3', lambda: self.update_text(name, display_label, '`3'), font_size_increase=0.5)
        self.make_generic_button(name, display_label, calculator_column5, key_strokes_binding_list, '0.5', lambda: self.update_text(name, display_label, '`0.5'), font_size_increase=0.5)
        self.make_generic_button(name, display_label, calculator_column5, key_strokes_binding_list, 'x', lambda: self.update_text(name, display_label, '`'), font_size_increase=0.5)
        
        self.make_generic_button(name, display_label, calculator_column6, key_strokes_binding_list, '^')
        self.make_generic_button(name, display_label, calculator_column6, key_strokes_binding_list, '%')
        self.make_generic_button(name, display_label, calculator_column6, key_strokes_binding_list, '(')
        self.make_generic_button(name, display_label, calculator_column6, key_strokes_binding_list, ')')
        
        self.make_generic_button(name, display_label, calculator_column7, key_strokes_binding_list, 'Update', lambda: self.send_graph_info_func(self.compile_calculator_text(display_label._text), self.funtion_calcs_info[name][self.color_entry_id].get(), index))
        
        self._slider_color_update(name)
    
    def _toogle_color_editor_state(self, name: str):
        info = self.funtion_calcs_info[name]
        
        color_reduc = 35
        
        if info[self.color_editor_enables_id]:
            for slider in info[self.color_sliders_id]:
                slider.configure(state='disabled', button_color=self._rgb_to_hex([max(0, v - color_reduc) for v in self._set_color(slider._button_color, 255, False)]))
            
            info[self.color_button_id].configure(state='disabled', fg_color=self._rgb_to_hex([max(0, v - color_reduc) for v in self._set_color(info[self.color_button_id]._fg_color, 255, False)]))
            info[self.color_entry_id].configure(state='disabled')
            info[self.toogle_state_button_id].configure(text='Activate Color Editor', text_color='white', hover_color=self._set_color('white', 50), fg_color='black')
            self.root.focus()
        else:
            for slider in info[self.color_sliders_id]:
                slider.configure(state='normal', button_color=self._rgb_to_hex([max(0, v + color_reduc) for v in self._set_color(slider._button_color, 255, False)]))
            info[self.color_button_id].configure(state='normal', fg_color=self._rgb_to_hex([min(255, v + color_reduc) for v in self._set_color(info[self.color_button_id]._fg_color, 255, False)]))
            info[self.color_entry_id].configure(state='normal')
            info[self.toogle_state_button_id].configure(text='Deactivate Color Editor', text_color='black', hover_color=self._set_color('black', 50), fg_color='white')
            info[self.color_entry_id].focus_force()
        info[self.color_editor_enables_id] = not info[self.color_editor_enables_id]
    
    def _slider_color_update(self, name: str):
        color_sliders = self.funtion_calcs_info[name][self.color_sliders_id]
        color_entry = self.funtion_calcs_info[name][self.color_entry_id]
        
        color_entry.delete(0, 'end')
        color_entry.insert(0, self._rgb_to_hex(list(slider.get() for slider in color_sliders)).lower())
        self._update_color(name, color_entry.get())
    
    def _update_color(self, name: str, color: ColorType):
        color_sliders = self.funtion_calcs_info[name][self.color_sliders_id]
        color_button = self.funtion_calcs_info[name][self.color_button_id]
        new_hover_color = self._set_color(color, 200)
        
        for slider in color_sliders:
            slider.configure(button_color=color, button_hover_color=new_hover_color)
        color_button.configure(fg_color=color)#, hover_color=new_hover_color)
    
    def _update_colors_from_entry(self, name: str):
        f_info = self.funtion_calcs_info[name]
        if f_info[self.frame_id] == self.current_frame:
            color_sliders = f_info[self.color_sliders_id]
            color_entry = f_info[self.color_entry_id]
            entry_color = color_entry.get()
            
            if f_info[self.color_entry_repr_id] == repr(self.root.focus_get()):
                if self._is_color(entry_color):
                    color = self._set_color(entry_color, 255, False)
                    for slider_index, slider in enumerate(color_sliders):
                        slider.set(color[slider_index])
                    self._update_color(name, self._rgb_to_hex(color))
            color_entry.after(100, lambda: self._update_colors_from_entry(name))
    
    def _add_sub_calc(self, name, temporary):
        self.current_menu_bar_frame = ctk.CTkFrame(self.frame_menu_bar, height=self.frame_menu_bar._desired_height, fg_color='transparent')
        self.current_menu_bar_frame.pack(side='left', fill='x', expand=True)
        _make_set_func_func = lambda name: lambda: self.set_func_focus(name)
        
        ctk.CTkButton(self.current_menu_bar_frame,
                      text=name,
                      command=_make_set_func_func(name),
                      fg_color='transparent',
                      corner_radius=0).place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor='center')
        
        if temporary:
            ctk.CTkButton(self.current_menu_bar_frame,
                          text='',
                          image=ctk.CTkImage(Image.open(r'images\cancel_icon.png'),
                                             size=(self.current_menu_bar_frame._desired_height // 4, self.current_menu_bar_frame._desired_height // 4)),
                          width=0,
                          height=0,
                          command=lambda: self.remove_function(name),
                          fg_color='transparent'
                        ).place(relx=1, rely=0, anchor='ne')
        
        self.current_frame = ctk.CTkFrame(self.root)
        self.current_frame.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor='center')
        self.funtion_calcs_info.update({name: {self.frame_id: self.current_frame, self.menu_bar_frame_id: self.current_menu_bar_frame, self.index_id: len(self.funtion_calcs_info), self.cursor_id: 0}})
        self._make_sub_calc(name)
        self.set_func_focus(name)
        
        self.menubar_bg_frame.lift()
    
    def add_sub_calc(self, temporary=True):
        name_dialog = ctk.CTkInputDialog(text='Menu name', title='Add new menu')
        
        new_frame_name = name_dialog.get_input()
        
        if new_frame_name and not new_frame_name.isspace() and new_frame_name not in self.funtion_calcs_info:
            self._add_sub_calc(new_frame_name, temporary)
        else:
            if new_frame_name:
                dialog.Dialog(None, {'title': 'Invalid Name Choosen',
                                    'text': (f'{new_frame_name} already exists, please choose another name'
                                            if new_frame_name in list(self.dislay_frames_dict.keys()) else
                                            'Name is inappropriate'),
                                    'bitmap': '',
                                    'default': 0,
                                    'strings': ('  Ok  ', )})
    
    def remove_function(self, name):
        main_frame = self.funtion_calcs_info[name][self.frame_id]
        keys = list(self.funtion_calcs_info.keys())
        index = keys.index(name)
        self.remove_graph_info_func(index)
        if self.current_frame == main_frame:
            self.set_func_focus(keys[index - 1])
        menu_frame_button_frame = self.funtion_calcs_info[name][self.menu_bar_frame_id]
        main_frame.destroy()
        menu_frame_button_frame.destroy()
        self.funtion_calcs_info.pop(name)
    
    def set_func_focus(self, name):
        for values in self.funtion_calcs_info.values():
            current_frame = values[self.frame_id]
            current_menu_bar_frame = values[self.menu_bar_frame_id]
            current_frame.place(relx=2, rely=2, anchor='nw')
            current_menu_bar_frame.configure(fg_color='transparent')
            for widg in current_menu_bar_frame.slaves():
                widg.configure(fg_color='transparent')
        self.current_frame = self.funtion_calcs_info[name][self.frame_id]
        self.current_menu_bar_frame = self.funtion_calcs_info[name][self.menu_bar_frame_id]
        keystroke_bindings = self.funtion_calcs_info[name][self.keystrokes_id]
        self.current_menu_bar_frame.configure(fg_color=ctk.ThemeManager.theme['CTkButton']['fg_color'])
        for widg in self.current_menu_bar_frame.slaves():
            widg.configure(fg_color=ctk.ThemeManager.theme['CTkButton']['fg_color'])
        self.current_frame.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor='center')
        for binding in keystroke_bindings:
            binding()
        self._update_colors_from_entry(name)
    
    def update_text(self, name: str, display_label: ctk.CTkLabel, text: str):
        if self.funtion_calcs_info[name][self.color_entry_repr_id] != repr(self.root.focus_get()):
            display_label.configure(text=display_label._text[:self.funtion_calcs_info[name][self.cursor_id]] + text + display_label._text[self.funtion_calcs_info[name][self.cursor_id]:])
            self.funtion_calcs_info[name][self.cursor_id] += len(text)
    
    def clear_all(self, name, display_label: ctk.CTkLabel):
        self.move_to_endings(name, display_label, 1)
        for _ in range(len(display_label._text)):
            self.backspace_text(name, display_label)
    
    def move_to_endings(self, name, display_label: ctk.CTkLabel, direction: Literal[-1, 1]):
        if direction > 0:
            for _ in range(len(display_label._text[self.funtion_calcs_info[name][self.cursor_id]:])):
                self.move_cursor(name, display_label, direction)
        elif direction < 0:
            for _ in range(len(display_label._text[:self.funtion_calcs_info[name][self.cursor_id]])):
                self.move_cursor(name, display_label, direction)
    
    def backspace_text(self, name: str, display_label: ctk.CTkLabel, skip_recurse: bool = False):
        if self.funtion_calcs_info[name][self.cursor_id] != 0:
            self.funtion_calcs_info[name][self.cursor_id] -= 1
            text = display_label._text.replace(self.cursor_char, '')
            display_label_text_list = list(text)
            display_label_text_list.pop(self.funtion_calcs_info[name][self.cursor_id])
            display_label_text_list.insert(self.funtion_calcs_info[name][self.cursor_id], self.cursor_char)
            new_text = ''.join(display_label_text_list)
            display_label.configure(text=new_text)
            there_was_a_space = False
            if not skip_recurse:
                if text[self.funtion_calcs_info[name][self.cursor_id]].isalpha() and text[self.funtion_calcs_info[name][self.cursor_id]] != self.x_id:
                    self.backspace_text(name, display_label)
                if text[self.funtion_calcs_info[name][self.cursor_id]].isspace():
                    there_was_a_space = True
                    self.backspace_text(name, display_label)
            if there_was_a_space:
                self.backspace_text(name, display_label, True)
    
    def move_cursor(self, name: str, display_label: ctk.CTkLabel, direction: Literal[-1, 1]):
        if (direction < 0 and self.funtion_calcs_info[name][self.cursor_id] != 0) or (direction > 0 and self.funtion_calcs_info[name][self.cursor_id] != len(display_label._text) - 1):
            init_text = list(display_label._text.replace(self.cursor_char, ''))
            self.funtion_calcs_info[name][self.cursor_id] += direction
            init_text.insert(self.funtion_calcs_info[name][self.cursor_id], self.cursor_char)
            text = ''.join(init_text)
            display_label.configure(text=text)
            if init_text[self.funtion_calcs_info[name][self.cursor_id]].isalpha():
                self.move_cursor(direction)
    
    def make_generic_button(self, name, display_label: ctk.CTkLabel, frame: ctk.CTkFrame, key_strokes_binding_list: list, text: str, func: Callable[[], None] | None = None, font_size_increase: int | None = None):
        constant_font_size_increase = 2
        
        font = ctk.CTkFont(size=int(ctk.ThemeManager.theme["CTkFont"]["size"] * constant_font_size_increase * (font_size_increase if font_size_increase is not None else 1)))
        ctk.CTkButton(frame, text=text, font=font, command=(lambda: self.update_text(name, display_label, text)) if func is None else func).pack(side='left', fill='both', expand=True, padx=10, pady=5)
        key_strokes_binding_list.append(lambda: self.root.bind(text, lambda m: self.update_text(name, display_label, text)))
    
    def compile_calculator_text(self, text: str):
        text = text.replace(self.cursor_char, '')
        text = text.replace('`', '**')
        text = text.replace(self.x_id, f'({self.x_id})')
        
        for func_index, func_name in enumerate(self.all_maths_funcs):
            text = text.replace(func_name, f'@{func_index}')
        ref_text = text
        for i, t in enumerate(text):
            if t == '@':
                if text[i - 1].isnumeric() and i != 0:
                    ref_text_list = list(ref_text)
                    ref_text_list.insert(i, ' * ')
                    ref_text = ''.join(ref_text_list)
                text = ref_text.replace(t + text[i + 1], f'__import__("math").{self.all_maths_funcs[int(text[i + 1])]}')
        
        l_text = list(text)
        for i, t in enumerate(l_text):
            if t == '(':
                if i - 1 > -1:
                    if l_text[i - 1] in (')', ) or l_text[i - 1].isnumeric():
                        l_text.insert(i, ' * ')
            elif t == ')':
                if i + 1 < len(l_text):
                    if l_text[i + 1] in ('(', '_') or l_text[i + 1].isnumeric():
                        l_text.insert(i + 1, ' * ')
        text = ''.join(l_text)
        
        left_bracket_difference = text.count('(') - text.count(')')
        if left_bracket_difference > 0:
            text += ')' * left_bracket_difference
        
        return text
    
    def get_graph_func(self, text: str):
        return lambda x: eval(text.replace(self.x_id, str(x)))
    
    def event_loop(self):
        if not Path(self.func_file).exists():
            self.root.quit()
        
        self.root.after(100, self.event_loop)
    
    def run(self):
        self.event_loop()
        self.root.mainloop()

class Graph:
    def __init__(self,
                 screen: pygame.Surface,
                 graph_functions_info: list[tuple[Callable, ColorType]],
                 plot_accuracy: int,
                 grid_size: Number,
                 grid_line_number_accuracy: int,
                 min_plot_rangex: int,
                 max_plot_rangex: int,
                 min_plot_rangey: int,
                 max_plot_rangey: int,
                 grid_line_color: ColorType,
                 grid_text_color: ColorType,
                 accesories_color: ColorType,
                 base_line_width: Number,
                 x_scale: Number = 1,
                 y_scale: Number = 1):
        self.screen = screen
        self.grid_text_color = grid_text_color
        self.grid_line_color = grid_line_color
        self.accesories_color = accesories_color
        self.base_line_width = base_line_width
        self.plot_accuracy = plot_accuracy
        self.grid_size = grid_size
        self.grid_line_number_accuracy = grid_line_number_accuracy
        self.x_scale = x_scale
        self.y_scale = y_scale
        
        self.mid_scr_point_x = self.screen.get_width() / 2
        self.mid_scr_point_y = self.screen.get_height() / 2
        
        self.mid_scr_ref_x = self.mid_scr_point_x
        self.mid_scr_ref_y = self.mid_scr_point_y
        
        self.mouse_pos = (0, 0)
        self.draw_plot_start_ref = (0, 0)
        self.draw_plot_start_ref = (0, 0)
        
        self.font = pygame.font.SysFont('Cambria', 20)
        
        self.min_draw_area_x = 0
        self.min_draw_area_y = 0
        self.max_draw_area_x = self.screen.get_width()
        self.max_draw_area_y = self.screen.get_height()
        
        self.init_min_plot_rangex = min_plot_rangex
        self.init_max_plot_rangex = max_plot_rangex
        self.init_min_plot_rangey = min_plot_rangey
        self.init_max_plot_rangey = max_plot_rangey
        
        self.min_plot_rangex = int(min_plot_rangex * self.x_scale * self.grid_size)
        self.max_plot_rangex = int(max_plot_rangex * self.x_scale * self.grid_size)
        self.min_plot_rangey = int(min_plot_rangey * self.y_scale * self.grid_size)
        self.max_plot_rangey = int(max_plot_rangey * self.y_scale * self.grid_size)
        
        self.min_scr_x_val = (self.mid_scr_point_x * 2) + ((self.min_plot_rangex / self.plot_accuracy) * self.x_scale * self.grid_size)
        self.max_scr_x_val = (self.max_plot_rangex / self.plot_accuracy) * self.x_scale * self.grid_size
        self.min_scr_y_val = (self.mid_scr_point_y * 2) + ((self.min_plot_rangey / self.plot_accuracy) * self.y_scale * self.grid_size)
        self.max_scr_y_val = (self.max_plot_rangey / self.plot_accuracy) * self.y_scale * self.grid_size
        
        self.graph_functions_info = graph_functions_info
        
        self.graph_func_amt = len(self.graph_functions_info)
        
        self.plot_info = []
        self.plotted_points = []
        self.orig_plotted_points = []
        self.plot_points = []
        self.orig_plotted_points_tracker = []
        
        self.show_cordinates_hovered = False
        self._has_toogled_show_coordinate = False
        self.show_mouse_xy_cordinates = False
        self._has_toogled_show_graph_xy_coordinate = False
        self.recalculate_everything = True
        self.recalculate_graph_line = False
        self.recalculate_text_and_gridlines = False
    
    def _sign(self, num: Number):
        return (num / abs(num)) if num != 0 else 1
    
    def _calculate_plot_vals(self, graph_info: list[Callable, ColorType], min_range: int, max_range: int):
        for i in range(min_range, max_range):
            try:
                x = i / self.plot_accuracy
                
                x_starting_plot = x * self.x_scale * self.grid_size
                x_ending_plot = (x - (1 / self.plot_accuracy)) * self.x_scale * self.grid_size
                
                for y, color in graph_info:
                    y_starting_plot = -(y(x) * self.y_scale * self.grid_size)
                    y_ending_plot = -(y(x - (1 / self.plot_accuracy)) * self.y_scale * self.grid_size)
                    
                    start_point = [x_starting_plot, y_starting_plot]
                    end_point = [x_ending_plot, y_ending_plot]
                    
                    self.plot_info.append([color, start_point, end_point, 4, 'plot line'])
            
            except (ValueError, ZeroDivisionError, OverflowError, TypeError):
                pass
    
    def _reposition_grid(self, min_range):
        for i in self.plot_info:
            if isinstance(i[0], pygame.Color | tuple | list | str):
                _, start, end, _, id_ = i
                if 'grid line' in id_:
                    d_X = end[0] - start[0]
                    d_Y = end[1] - start[1]
                    if start[1] != end[1]:
                        if 'x' in id_:
                            start[1] -= d_Y + (((min_range / self.plot_accuracy) * self.grid_size) * 2)
                            end[1] -= d_Y + (((min_range / self.plot_accuracy) * self.grid_size) * 2)
                    else:
                        if 'y' in id_:
                            start[0] += d_X + (((min_range / self.plot_accuracy) * self.grid_size) * 2)
                            end[0] += d_X + (((min_range / self.plot_accuracy) * self.grid_size) * 2)
    
    def _add_text_and_gridlines(self, min_rangex, max_rangex, min_rangey, max_rangey):
        max_end_of_graph_y = ((max_rangex * self.x_scale) / self.plot_accuracy) * self.grid_size
        min_end_of_graph_y = (min_rangex / self.plot_accuracy) * self.grid_size
        
        max_cut_off_rangex = (max_rangex * self.x_scale) / self.grid_size
        min_cut_off_rangex = (min_rangex * self.x_scale) / self.grid_size
        
        for i in range(min_rangex, max_rangex):
            x = i / self.plot_accuracy
            
            x_plot = x * self.x_scale * self.grid_size
            
            if min_cut_off_rangex < x < max_cut_off_rangex:
                if x != 0:
                    if (x / self.grid_line_number_accuracy).is_integer():
                        self.plot_info.append([self.grid_line_color, [x_plot, min_end_of_graph_y], [x_plot, max_end_of_graph_y], int(self.base_line_width / 2), 'grid linex'])
                        text = self.font.render(str(int(x)), False, self.grid_text_color)
                        self.plot_info.append((text, [x_plot - (text.get_width() / 2) + int(self.base_line_width / 2), 0], 'textx'))
                    elif (x / (self.grid_line_number_accuracy / 2)).is_integer():
                        self.plot_info.append([self.grid_line_color, [x_plot, min_end_of_graph_y], [x_plot, max_end_of_graph_y], max(int(self.base_line_width / 6), 1), 'grid linex'])
                else:
                    self.plot_info.append([self.grid_line_color, [x_plot, min_end_of_graph_y], [x_plot, max_end_of_graph_y], self.base_line_width, 'grid linex'])
        
        min_rangey = -max_rangey
        max_rangey = -min_rangey
        
        max_end_of_graph_x = (max_rangey / self.plot_accuracy) * self.grid_size
        min_end_of_graph_x = ((min_rangey * self.y_scale) / self.plot_accuracy) * self.grid_size
        
        max_cut_off_rangey = (max_rangey * self.y_scale) / self.grid_size
        min_cut_off_rangey = (min_rangey * self.y_scale) / self.grid_size
        
        for i in range(min_rangey, max_rangey):
            y = i / self.plot_accuracy
            
            y_plot = y * self.y_scale * self.grid_size
            
            if min_cut_off_rangey < y < max_cut_off_rangey:
                if y != 0:
                    if (y / self.grid_line_number_accuracy).is_integer():
                        self.plot_info.append([self.grid_line_color, [min_end_of_graph_x, y_plot], [max_end_of_graph_x , y_plot], int(self.base_line_width / 2), 'grid liney'])
                        text = self.font.render(str(int(-y)), False, self.grid_text_color)
                        self.plot_info.append((text, [0, y_plot - (text.get_height() / 2) + int(self.base_line_width / 2)], 'texty'))
                    elif (y / (self.grid_line_number_accuracy / 2)).is_integer():
                        self.plot_info.append([self.grid_line_color, [min_end_of_graph_x, y_plot], [max_end_of_graph_x, y_plot], max(int(self.base_line_width / 6), 1), 'grid liney'])
                else:
                    self.plot_info.append([self.grid_line_color, [min_end_of_graph_x, y_plot], [max_end_of_graph_x, y_plot], self.base_line_width, 'grid liney'])
    
    def _add_plotted_point(self):
        for orig_plot_point in self.orig_plotted_points:
            self._plot(*orig_plot_point)
        
        for blit_index in range(len(self.plot_points)):
            blit_point, color, x_thickness, x_half_length = self.plot_points[blit_index]
            criss = [color, [blit_point[0] - x_half_length, blit_point[1] - x_half_length], [blit_point[0] + x_half_length, blit_point[1] + x_half_length], x_thickness, 'plot line']
            self.plot_info.append(criss)
            cross = [color, [blit_point[0] + x_half_length, blit_point[1] - x_half_length], [blit_point[0] - x_half_length, blit_point[1] + x_half_length], x_thickness, 'plot line']
            self.plot_info.append(cross)
        
        self.plot_points = []
    
    def _update_mid_scr_pos(self, continue_moving_screen):
        if pygame.mouse.get_pressed()[0] and continue_moving_screen:
            self.mid_scr_point_x = self.mid_scr_rec_x + (self.mouse_pos[0] - self.mouse_pos_ref[0])
            self.mid_scr_point_y = self.mid_scr_rec_y + (self.mouse_pos[1] - self.mouse_pos_ref[1])
        else:
            self.mid_scr_rec_x = self.mid_scr_point_x
            self.mid_scr_rec_y = self.mid_scr_point_y
            self.mouse_pos_ref = self.mouse_pos
        
        self.mid_scr_point_x = pygame.math.clamp(self.mid_scr_point_x, self.min_scr_x_val, self.max_scr_x_val)
        self.mid_scr_point_y = pygame.math.clamp(self.mid_scr_point_y, self.min_scr_y_val, self.max_scr_y_val)
    
    def _update_ui(self):
        if self.keys[pygame.K_c]:
            if self._has_toogled_show_coordinate:
                self.show_cordinates_hovered = not self.show_cordinates_hovered
                self._has_toogled_show_coordinate = False
        else:
            self._has_toogled_show_coordinate = True
        
        if self.keys[pygame.K_p]:
            if self._has_toogled_show_graph_xy_coordinate:
                self.show_mouse_xy_cordinates = not self.show_mouse_xy_cordinates
                self._has_toogled_show_graph_xy_coordinate = False
        else:
            self._has_toogled_show_graph_xy_coordinate = True
        
        x_coord = ((self.mouse_pos[0] - self.mid_scr_point_x) / self.grid_size) / self.x_scale
        y_coord = (-(self.mouse_pos[1] - self.mid_scr_point_y) / self.grid_size) / self.y_scale
        mouse_view_coordinate = x_coord, y_coord
        
        if self.show_cordinates_hovered:
            text_surf = self.font.render(str((mouse_view_coordinate[0], mouse_view_coordinate[1])), True, self.accesories_color)
            text_rect = pygame.Rect(self.mouse_pos[0] - text_surf.get_width(), self.mouse_pos[1] - text_surf.get_height(), *text_surf.get_size())
            self.screen.blit(text_surf, text_rect)
        
        if self.show_mouse_xy_cordinates:
            for graph_function, color in self.graph_functions_info:
                try:
                    x = self.mouse_pos[0]
                    y = self.mid_scr_point_y - (graph_function(mouse_view_coordinate[0]) * self.y_scale * self.grid_size)
                    text_surf = self.font.render(str((round(mouse_view_coordinate[0], 2), round((self.mid_scr_point_y - y) / (self.grid_size * self.y_scale), 2))), True, color)
                    line_rect = pygame.draw.line(self.screen, color, (x - 1, y - 1), (x - 1, self.mouse_pos[1] - 1), 4)
                    self.screen.blit(text_surf, line_rect.midright)
                    pygame.draw.circle(self.screen, color, (x, y), 5)
                except (ValueError, ZeroDivisionError, OverflowError, TypeError):
                    pass
            
            pygame.draw.circle(self.screen, self.accesories_color, self.mouse_pos, 5)
    
    def _draw_grid(self):
        for i in self.plot_info:
            if isinstance(i[0], pygame.Color | tuple | list | str):
                color, start, end, width, id_ = i
                if 'x' in id_:
                    if 0 < start[0].real + self.mid_scr_point_x < self.screen.get_width() or 0 < end[0].real + self.mid_scr_point_x < self.screen.get_width():
                        pygame.draw.line(self.screen, color, (start[0].real + self.mid_scr_point_x, 0), (end[0].real + self.mid_scr_point_x, self.screen.get_height()), width)
                elif 'y' in id_:
                    if 0 < start[1].real + self.mid_scr_point_y < self.screen.get_height() or 0 < end[1].real + self.mid_scr_point_y < self.screen.get_height():
                        pygame.draw.line(self.screen, color, (0, start[1].real + self.mid_scr_point_y), (self.screen.get_width(), end[1].real + self.mid_scr_point_y), width)
                else:
                    if 0 < start[0].real + self.mid_scr_point_x < self.screen.get_width() or 0 < end[0].real + self.mid_scr_point_x < self.screen.get_width() and 0 < start[1].real + self.mid_scr_point_y < self.screen.get_height() or 0 < end[1].real + self.mid_scr_point_y < self.screen.get_height():
                        pygame.draw.line(self.screen, color, (start[0].real + self.mid_scr_point_x, start[1].real + self.mid_scr_point_y), (end[0].real + self.mid_scr_point_x, end[1].real + self.mid_scr_point_y), width)
            else:
                surf, pos, _ = i
                if 0 < pos[0].real + self.mid_scr_point_x < self.screen.get_width() and 0 < pos[1].real + self.mid_scr_point_y < self.screen.get_height():
                    self.screen.blit(surf, (pos[0].real + self.mid_scr_point_x, pos[1].real + self.mid_scr_point_y))
    
    def _plot(self, coord: tuple[float, float], color: ColorType, x_thickness: float, x_half_length: float):
        x, y = coord
        
        x_plot = x * self.x_scale * self.grid_size
        y_plot = -y * self.y_scale * self.grid_size
        
        point = x_plot, y_plot
        self.plot_points.append((point, color, x_thickness, x_half_length))
    
    def configure(self, **kwargs):
        if 'graph_functions_info' in kwargs:
            graph_functions_info = kwargs.pop('graph_functions_info')
            if graph_functions_info is not None:
                self.recalculate_everything = True
                self.graph_functions_info = graph_functions_info
        
        if 'plot_accuracy' in kwargs:
            plot_accuracy = kwargs.pop('plot_accuracy')
            if plot_accuracy is not None:
                self.recalculate_everything = True
                self.plot_accuracy = plot_accuracy
        
        if 'grid_size' in kwargs:
            grid_size = kwargs.pop('grid_size')
            if grid_size is not None:
                self.recalculate_everything = True
                self.grid_size = grid_size
        
        if 'grid_line_number_accuracy' in kwargs:
            grid_line_number_accuracy = kwargs.pop('grid_line_number_accuracy')
            if grid_line_number_accuracy is not None:
                self.recalculate_text_and_gridlines = True
                self.grid_line_number_accuracy = grid_line_number_accuracy
        
        if 'grid_line_color' in kwargs:
            grid_line_color = kwargs.pop('grid_line_color')
            if grid_line_color is not None:
                self.recalculate_text_and_gridlines = True
                self.grid_line_color = grid_line_color
        
        if 'grid_text_color' in kwargs:
            grid_text_color = kwargs.pop('grid_text_color')
            if grid_text_color is not None:
                self.recalculate_text_and_gridlines = True
                self.grid_text_color = grid_text_color
        
        if 'accesories_color' in kwargs:
            accesories_color = kwargs.pop('accesories_color')
            if accesories_color is not None:
                self.recalculate_text_and_gridlines = True
                self.accesories_color = accesories_color
        
        if 'base_line_width' in kwargs:
            base_line_width = kwargs.pop('base_line_width')
            if base_line_width is not None:
                self.recalculate_text_and_gridlines = True
                self.base_line_width = base_line_width
        
        if 'x_scale' in kwargs:
            x_scale = kwargs.pop('x_scale')
            if x_scale is not None:
                self.recalculate_everything = True
                self.x_scale = x_scale
        
        if 'y_scale' in kwargs:
            y_scale = kwargs.pop('y_scale')
            if y_scale is not None:
                self.recalculate_everything = True
                self.y_scale = y_scale
    
    def add_y_func(self, func: Callable[[float], float], color: ColorType):
        self.recalculate_everything = True
        self.graph_functions_info.append([func, color])
     
    def plot(self, coord: tuple[float, float], color: ColorType, x_thickness: float = 2, x_half_length: float = 4):
        self.orig_plotted_points.append((coord, color, x_thickness, x_half_length))
    
    def plot_y(self, x: float, graphfuncindex: int, x_thickness: float = 2, x_half_length: float = 4):
        graph_func, color = self.graph_functions_info[graphfuncindex]
        y = graph_func(x)
        self.plot((x, y), color, x_thickness, x_half_length)
    
    def update(self, continue_moving_screen: bool = True):
        self.mouse_pos = pygame.mouse.get_pos()
        self.keys = pygame.key.get_pressed()
        
        if self.recalculate_everything:
            self.plot_info = []
            self._add_text_and_gridlines(self.min_plot_rangex, self.max_plot_rangex, self.min_plot_rangey, self.max_plot_rangey)
            self._calculate_plot_vals(self.graph_functions_info, max(self.min_plot_rangex, self.min_plot_rangey), min(self.max_plot_rangex, self.max_plot_rangey))
            self._add_plotted_point()
            self._reposition_grid(self.min_plot_rangex)
            
            self.orig_plotted_points_tracker = self.orig_plotted_points
            self.recalculate_everything = False
        else:
            if self.orig_plotted_points_tracker != self.orig_plotted_points:
                self._add_plotted_point()
                self.orig_plotted_points_tracker = self.orig_plotted_points
            if self.recalculate_graph_line:
                for graph_function, color in self.graph_functions_info:
                    self._calculate_plot_vals(graph_function, max(self.min_plot_rangex, self.min_plot_rangey), min(self.max_plot_rangex, self.max_plot_rangey), color)
                self.recalculate_graph_line = False
            if self.recalculate_text_and_gridlines:
                self._add_text_and_gridlines(self.min_plot_rangex, self.max_plot_rangex, self.min_plot_rangey, self.max_plot_rangey)
                self.recalculate_text_and_gridlines = False
        
        self._update_mid_scr_pos(continue_moving_screen)
        
        self._update_ui()
        
        self._draw_grid()

class GraphApp:
    def __init__(self, function_file: FileType):
        pygame.init()
        self.screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
        pygame.display.set_caption('Graph Viewer')
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont('Arial', 20)
        
        self.function_file = function_file
        
        self.functions_tracker = []
        
        self.graph = Graph( self.screen,
                            graph_functions_info = [],
                            plot_accuracy = 20,
                            grid_size = 10,
                            grid_line_number_accuracy = 10,
                            min_plot_rangex = -100,
                            max_plot_rangex = 100,
                            min_plot_rangey = -100,
                            max_plot_rangey = 100,
                            grid_line_color = 'green',
                            grid_text_color = 'white',
                            accesories_color = 'red',
                            base_line_width = 4,
                            x_scale = 1,
                            y_scale = 1,
                            )
    
    def event_loop(self, event):
        self.keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            self.quit()
        
    def quit(self):
        if Path(self.function_file).exists():
            os.remove(self.function_file)
        pygame.quit()
        sys.exit()
        
    def app_loop(self):
        font_surf = self.font.render(f'FPS: {int(self.clock.get_fps())}', True, 'white')
        topleft = self.screen.get_width() - font_surf.get_width(), self.screen.get_height() - font_surf.get_height()
        self.screen.blit(font_surf, topleft)
        
        if not Path(self.function_file).exists():
            self.quit()
        with open(self.function_file) as func_file:
            func_strings = json.loads(func_file.read())
            if self.functions_tracker != func_strings:
                def make_func(s): return lambda x: eval(s.replace('x', str(x)))
                self.functions = [(make_func(s), color) for s, color in func_strings]
                self.graph.configure(graph_functions_info=self.functions)
                self.functions_tracker = func_strings
        
        self.graph.update()
    
    def run(self):
        while True:
            self.delta_time = self.clock.tick(FPS)
            self.screen.fill(SCREEN_BG_COLOR)
            
            for event in pygame.event.get():
                self.event_loop(event)
            
            self.app_loop()
            
            pygame.display.update()

