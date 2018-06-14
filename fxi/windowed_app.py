import tkinter
from tkinter import ttk

from .base import BaseApp


class WindowedApp(BaseApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = self.get_main_window()

    def get_main_window(self):
        window = tkinter.Tk()
        window.title("fxi")
        window.geometry('800x600')
        window.configure(background='white')

        font_family = 'Georgia'
        base_font_size = 14
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background='white')
        style.configure('.', foreground='black')
        style.configure('.', font=(font_family, base_font_size))
        style.configure('TNotebook', font=('Terminus', base_font_size), background='gray')
        style.configure('cell.TLabel', font=('Terminus', base_font_size))
        style.configure('header.TLabel', font=('Terminus', base_font_size, 'bold'))
        style.configure('h3.TLabel', font=(font_family, base_font_size, 'bold'))
        style.configure('h2.TLabel', font=(font_family, base_font_size + 2, 'bold'))
        style.configure('h1.TLabel', font=(font_family, base_font_size + 4, 'bold'))
        style.configure('status.TLabel', font=('Terminus', 12))
        return window
