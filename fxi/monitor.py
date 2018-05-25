import tkinter
from tkinter import ttk


class Monitor(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.lines = []
        self.alive = True

        super().__init__(parent.tab.interior, *args, **kwargs)
        self.configure(relief=tkinter.SUNKEN)

    def write(self, message, indentation=0):
        if not self.alive:
            return

        if indentation:
            spacer = '-' * (indentation - 1)
            formatted_message = f'+{spacer}{message}'
        else:
            formatted_message = f'{message}'

        width = self.master.winfo_width()
        label = ttk.Label(
            self,
            text=formatted_message,
            anchor=tkinter.W,
            justify=tkinter.LEFT,
            wraplength=width
        )
        label.pack(expand=True, fill=tkinter.X)
        self.lines.append(label)
        self.master.master.master.page_down()  # XXX

    def close(self):
        self.alive = False
        self.destroy()

    def h1(self, title):
        label = ttk.Label(
            self,
            text=f'{title}',
            anchor=tkinter.W,
            justify=tkinter.LEFT,
            font=("Terminus", 14, "bold")
        )

        label.pack(expand=True, fill=tkinter.X)

    def hr(self):
        self.write('-' * 50)
