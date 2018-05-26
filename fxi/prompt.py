import time
import tkinter
from tkinter.ttk import Label


class Prompt(Label):
    def __init__(self, command_line, parent):
        self.command_line = command_line

        self.content = tkinter.StringVar()
        self.reset()

        self.answer = None

        super().__init__(
            parent,
            textvariable=self.content,
            anchor=tkinter.W,
            justify=tkinter.LEFT,
            font=("Terminus", 14)
        )

    def reset(self):
        self.content.set('> ')

    def ask(self, question, hidden=False):
        self.content.set(f'{question}: ')
        self.command_line.callback = self.answer_callback

        if hidden:
            self.command_line.configure(show="-")

        self.answer = None
        while self.command_line.parent.alive and self.answer is None:
            time.sleep(0.1)

        self.command_line.configure(show='')

        return self.answer

    def answer_callback(self, answer):
        self.command_line.callback = None
        self.answer = answer
        self.reset()
