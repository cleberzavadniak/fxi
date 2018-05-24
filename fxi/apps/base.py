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

    def init(self):
        pass

    def new_thread(self, method, args=None, kwargs=None):
        args = args or ()
        kwargs = kwargs or {}
        t = threading.Thread(target=method, args=args, kwargs=kwargs)
        t.start()
        return t

    def info(self, message):
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
        if self.main_list:
            t = threading.Thread(target=self.main_list.handle_command, args=[command])
            t.start()
            return
        print('AppBase.handle_command:', command)

    def open_monitor(self, name=None):
        if self.current_monitor:
            self.current_monitor.close()

        monitor = Monitor(self.tab.interior, relief=tkinter.RIDGE)
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
