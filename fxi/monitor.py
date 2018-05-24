import tkinter
from tkinter import ttk
from fxi.widgets.scrollables import VerticalScrolledFrame


class Monitor(VerticalScrolledFrame):
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
            self.interior,
            text=formatted_message,
            anchor=tkinter.W,
            justify=tkinter.LEFT,
        )
        label.grid(
            column=1,
            row=len(self.lines),
            sticky=tkinter.W
        )
        self.lines.append(label)
        self.canvas.yview_scroll(1, "pages")
        self.canvas.update()

    def close(self):
        self.alive = False
        self.destroy()
