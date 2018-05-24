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
        self.main_window = self.get_main_window()

        self.apps = []
        self.available_apps = {}
        self.current_app = None

        self.notebook = Notebook(self)
        self.notebook.pack(expand=1, fill='both')

        self.commands_frame = ttk.Frame()
        self.commands_frame.pack(fill=tkinter.X)
        self.command_line = CommandLine(self, self.commands_frame)
        self.prompt = Prompt(self.command_line, self.commands_frame)
        self.prompt.pack(side=tkinter.LEFT)
        self.command_line.pack(side=tkinter.LEFT, expand=True, fill=tkinter.X)

        self.status_bar = ttk.Frame(self.main_window)
        self.status_bar.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        self.status = ttk.Label(self.status_bar, relief=tkinter.SUNKEN, anchor=tkinter.W)
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

        style = ttk.Style()
        style.theme_use('clam')
        return window

    def load_apps(self):
        path = PosixPath(os.environ['HOME']) / 'fxi-apps'  # TODO: allow user to change it
        sys.path.append(str(path))

        for entry in path.glob('*'):
            if not entry.is_dir():
                continue

            initfile = entry / '__init__.py'
            if not initfile.exists():
                continue

            app_name = entry.name
            try:
                module = importlib.import_module(app_name)
            except ModuleNotFoundError:
                print('ModuleNotFoundError:', app_name)
                continue
            try:
                the_app_class = getattr(module, 'App')
            except AttributeError:
                continue
            self.available_apps[app_name] = the_app_class
            print('Loaded app:', app_name)

        main_app = MainApp(self)
        main_app.init()
        self.apps.append(main_app)
        self.current_app = main_app

    def open_app(self, name):
        app_class = self.available_apps[name]
        app = app_class(self)
        app.init()

        self.apps.append(app)
        self.current_app = app

        app.render_app()
        self.notebook.focus_on_app(app)

    def render_apps(self):
        for app in self.apps:
            app.render_app()

    def stop_apps(self):
        print('Stopping apps...')
        for app in self.apps:
            app.alive = False

    def start(self):
        self.load_apps()
        self.render_apps()
        self.command_line.focus_set()
        self.main_window.mainloop()
        self.stop_apps()
