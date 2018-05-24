import re
import threading
import tkinter
from tkinter.ttk import Entry


class CommandLine(Entry):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.bind("<Return>", self.enter_callback)

        self.callback = None

        for key in "cdrw1234567890":
            self.bind(key, self.keys_callback)

    def clear(self):
        self.delete(0, tkinter.END)

    def enter_callback(self, event):
        cmd = self.get()
        self.clear()

        if self.callback:
            self.callback(cmd)
            return

        self.handle_command(cmd)

    def keys_callback(self, event):
        if event.state == 4:  # Control
            key = event.keysym
            if key == 'c':
                self.clear()
                return

            elif key == 'd':
                self.master.quit()
                return

            elif key == 'r':
                if self.parent.current_app:
                    self.parent.current_app.refresh()
                    return

            elif key == 'w':
                if self.parent.current_app:
                    app = self.parent.current_app
                    app.close_monitor()

            elif key in '123456789':
                # Move all this code to a method in `fxi`.
                app = self.parent.apps[int(key) - 1]
                self.parent.notebook.focus_on_app(app)
                self.parent.current_app = app

            else:
                print('Not found:', key)

    def handle_command(self, command):
        if command[0] == ':':
            cmd = command[1:]

            if cmd == 'q':
                print('Quitting.')
                self.master.quit()
                return

        cmd, *args = re.split(r'\s+', command)

        if cmd in self.parent.available_apps:
            t = threading.Thread(target=self.parent.open_app, args=[cmd])
            t.start()
            return

        if self.parent.current_app:
            self.parent.current_app.handle_command(command)
