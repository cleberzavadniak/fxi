from os import environ
from pathlib import PosixPath
import re
import shelve
import threading
import tkinter
from tkinter import ttk

from fxi.widgets.scrollables import VerticalScrolledFrame
from fxi.monitor import Monitor


class AppBase:
    title = 'App'

    def __init__(self, fxi):
        self.fxi = fxi
        self.notebook = fxi.notebook
        self.tab = VerticalScrolledFrame(
            self.notebook,
            relief=tkinter.SUNKEN,
        )
        self.alive = True

        self.main_list = None
        self.current_monitor = None

        self.load_config()

    def load_config(self):
        basedir = PosixPath(environ['HOME']) / '.config' / 'fxi' / 'apps'
        basedir.mkdir(exist_ok=True, parents=True)
        path = basedir / self.title
        self.config = shelve.open(str(path))
        self.unsaved_config = {}

    def init(self):
        pass

    def quit(self):
        self.alive = False
        self.config.close()

    def new_thread(self, method, args=None, kwargs=None):
        args = args or ()
        kwargs = kwargs or {}
        t = threading.Thread(target=method, args=args, kwargs=kwargs)
        t.start()
        return t

    def info(self, message=None):
        self.fxi.info(message)

    def render(self):
        pass

    def render_app(self):
        self.render()
        self.notebook.add_app(self)
        return self.tab

    def refresh(self):
        if self.main_list:
            self.main_list.refresh()

    def handle_command(self, command):
        cmd, *args = re.split(r'\s+', command)
        method_name = f'cmd__{cmd}'
        method = getattr(self, method_name, None)
        if method:
            t = threading.Thread(target=method, args=args)
            t.start()
            return

        print('AppBase.handle_command:', command)

    def open_monitor(self, name=None):
        if self.current_monitor:
            self.current_monitor.close()

        monitor = Monitor(self, relief=tkinter.RIDGE)
        if name:
            monitor.h1(name)
        monitor.pack(expand=True, fill='both')
        self.current_monitor = monitor
        return monitor

    def close_monitor(self):
        if self.current_monitor:
            self.current_monitor.close()

    def h1(self, title):
        label = ttk.Label(
            self.tab.interior,
            text=f'{title}',
            anchor=tkinter.W,
            justify=tkinter.LEFT,
            font=("Terminus", 16, "bold")
        )

        label.pack(expand=True, fill='x')

    def get_config_or_ask(self, key, hidden=False, label=None, default=None):
        if key in self.config:
            return self.config[key]

        label = label or key

        if default is not None:
            label = f'{label} [{default}]'

        value = self.fxi.prompt.ask(label, hidden=hidden) or default
        self.unsaved_config[key] = value
        return value

    def persist_unsaved_config(self):
        for key, value in tuple(self.unsaved_config.items()):
            self.config[key] = value
            del self.unsaved_config[key]
