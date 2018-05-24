from tkinter import ttk


class Notebook(ttk.Notebook):
    def __init__(self, fxi, *args, **kwargs):
        self.fxi = fxi
        super().__init__(fxi.main_window, *args, **kwargs)

    def focus_on_app(self, app):
        self.focus_on_tab(app.tab)

    def focus_on_tab(self, tab):
        tab_key = tab.winfo_pathname(tab.winfo_id())
        self.select(tab_key)

    def add_app(self, app):
        self.add(app.tab, text=app.title)
