from functools import partial
import tkinter
from tkinter.ttk import Label


class Prompt(Label):
    def __init__(self, command_line, parent):
        self.command_line = command_line

        self.content = tkinter.StringVar()
        self.reset()

        super().__init__(
            parent,
            textvariable=self.content,
            anchor=tkinter.W,
            justify=tkinter.LEFT,
            font=("Terminus", 14)
        )

    def reset(self):
        self.content.set('> ')

    def ask(self, question, callback):
        self.content.set(f'{question}: ')
        self.command_line.callback = partial(self.answer_callback, callback)

    def answer_callback(self, callback, answer):
        self.command_line.callback = None
        self.reset()
        callback(answer)
