import importlib
from pathlib import PosixPath
import os
import sys
import tkinter
from tkinter import ttk

from .command_line import CommandLine
from .prompt import Prompt
from .apps.main import App as MainApp
from .notebook import Notebook


class FXI:
    def __init__(self):
        self.alive = False
        self.main_window = self.get_main_window()

        self.available_apps = []
        self.running_apps = {}
        self.current_app = None

        self.notebook = Notebook(self)
        self.notebook.pack(expand=1, fill='both')

        self.commands_frame = ttk.Frame()
        self.commands_frame.pack(fill=tkinter.X)
        self.command_line = CommandLine(self, self.commands_frame)
        self.prompt = Prompt(self.command_line, self.commands_frame)
        self.prompt.pack(side=tkinter.LEFT)
        self.command_line.pack(side=tkinter.LEFT, expand=True, fill=tkinter.X)

        self.status_bar = ttk.Frame(self.main_window, style='status.TFrame')
        self.status_bar.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        self.status = ttk.Label(
            self.status_bar,
            relief=tkinter.SUNKEN,
            anchor=tkinter.W,
            style='status.TLabel'
        )
        self.status['text'] = "Welcome"
        self.status.pack(fill=tkinter.X)

    def info(self, message):
        # TODO:
        # 1- Save historic data for messages.
        # 2- Count how many time each message was on
        # screen (so we know how much "Loading..."
        # took to finish).
        message = message or '-'
        self.status['text'] = message

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

    def locate_apps(self):
        path = PosixPath(os.environ['HOME']) / 'fxi-apps'  # TODO: allow user to change it
        sys.path.append(str(path))

        for entry in path.glob('fx*'):
            if not entry.is_dir():
                continue

            initfile = entry / '__init__.py'
            if not initfile.exists():
                continue

            app_name = entry.name[2:]
            self.available_apps.append(app_name)

        main_app = MainApp(self)
        main_app.init()
        self.running_apps['main'] = main_app
        main_app.render_app()
        self.current_app = 'main'

    def get_app_class(self, app_name):
        module_name = f'fx{app_name}'
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as ex:
            print(f'ModuleNotFoundError: {ex}')
            return
        try:
            the_app_class = getattr(module, 'App')
        except AttributeError as ex:
            print(f' {app_name}: AttributeError: {ex}')
            return

        the_app_class._module_reference = module
        return the_app_class

    def open_app(self, name):
        app_class = self.get_app_class(name)
        app = app_class(self)
        app.init()

        app.render_app()
        self.notebook.focus_on_app(app)
        self.current_app = name
        self.running_apps[name] = app

    def unload_app(self, name):
        app = self.running_apps[name]
        app.quit()
        del self.running_apps[name]

    def stop_apps(self):
        print('Stopping apps...')
        for app in self.running_apps.values():
            app.quit()

    def start(self, command_line_arg=None):
        self.alive = True
        self.locate_apps()
        self.command_line.focus_set()
        if command_line_arg:
            self.command_line.handle_command(command_line_arg)
        self.main_window.mainloop()
        self.alive = False
        self.stop_apps()
