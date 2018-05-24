import tkinter
from tkinter import ttk


class Monitor(ttk.Frame):
    def __init__(self, *args, **kwargs):
        self.lines = []
        self.alive = True

        super().__init__(*args, **kwargs)
        self.configure(relief=tkinter.SUNKEN)

    def write(self, message, indentation=0):
        if not self.alive:
            return

        if indentation:
            spacer = '-' * (indentation - 1)
            formatted_message = f'+{spacer}{message}'
        else:
            formatted_message = f'{message}'
        label = ttk.Label(
            self,
            text=formatted_message,
            anchor=tkinter.W,
            justify=tkinter.LEFT,
            wraplength=self.master.winfo_reqwidth()
        )
        label.grid(
            column=1,
            row=len(self.lines) + 1,
            sticky=tkinter.W
        )
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

        label.grid(
            column=0,
            row=0,
            columnspan=5
        )

    def hr(self):
        self.write('-' * 50)
