import tkinter
from tkinter import ttk


class Entry:
    def __init__(self, parent, index, data):
        self.parent = parent
        self.index = index
        self.data = data

        self.widgets = []
        self.marker = None

    def render(self):
        frame = self.parent.frame

        label = ttk.Label(frame, text=f'{self.index}')
        label.grid(
            column=0,
            row=self.index + 1,
            padx=10
        )
        self.index_marker = label
        self.widgets.append(label)

        total_width = self.parent.parent.tab.master.winfo_width()
        width = total_width / len(self.parent.headers)
        for cell_index, cell in enumerate(self.parent.cells):
            for value_index, value in enumerate(self.data[key] for key in cell):
                label = ttk.Label(
                    frame,
                    text=f'{value}',
                    anchor=tkinter.W,
                    justify=tkinter.LEFT,
                    font=("Terminus", 12),
                    wraplength=width
                )
                label.grid(
                    column=cell_index + 1,
                    row=self.index + 1,
                    padx=10,
                    pady=1,
                    sticky=tkinter.W
                )
                self.widgets.append(label)

    def destroy(self):
        for widget in self.widgets:
            for slave in widget.grid_slaves():
                slave.destroy()
            widget.destroy()
        self.widgets = []

    def refresh(self, data=None):
        if data:
            self.data = data
        self.destroy()
        self.render()

    def mark_as(self, mark):
        if self.index_marker:
            if mark == 'loading':
                new_text = "*"
            else:
                new_text = mark

            self.index_marker['text'] = new_text
            self.index_marker.update()


class EntryCommand:
    def __init__(self, function, name=None, description=None):
        self.name = name or function.__name__
        self.function = function
        self.description = description


class MainList:
    def __init__(self, parent, cells, headers=None):
        self.parent = parent
        frame = ttk.Frame(parent.tab.interior, borderwidth=1, relief=tkinter.RIDGE)
        self.frame = frame
        self.cells = cells
        self.headers = headers or []
        self.commands = {}

        self.entries = []

    def render(self, data):
        label = ttk.Label(self.frame, text='#')
        label.grid(column=0, row=0)

        for index, header in enumerate(self.headers):
            label = ttk.Label(
                self.frame,
                text=header,
                font=("Terminus", 14),
            )
            label.grid(
                column=index + 1,
                row=0,
                padx=10,
                pady=(0, 5)
            )

        if isinstance(data, dict):
            values = data.values()
        else:
            values = data

        for row_index, entry_data in enumerate(values):
            entry = Entry(self, row_index, entry_data)
            self.entries.append(entry)
            entry.render()

        self.frame.pack(expand=True, fill='x')

    def refresh(self):
        for entry in self.entries:
            entry.mark_as('loading')
            entry.refresh()

    def clear(self):
        for widget in self.frame.grid_slaves():
            widget.destroy()
        self.frame.pack_forget()
        self.entries = []

    def add_entry_command(self, function, name=None, description=None):
        self.commands[name] = EntryCommand(function, name, description)
