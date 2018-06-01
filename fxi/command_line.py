import importlib
import re
import threading
import tkinter
from tkinter.ttk import Entry


def bind_key(keysym, ctrl):
    def decorator(method):
        def new_method(self, event):
            if ctrl and not event.state == 4:
                return
            return method(self, event)

        new_method.keysym = keysym
        new_method.modifier_control = ctrl
        return new_method
    return decorator


# TODO: too much stuff is being made here in name
# of `self.parent`. Move it all to parent object
# class itself.
class CommandLine(Entry):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.bind("<Return>", self.enter_callback)

        self.callback = None

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            keysyms = getattr(attr, 'keysym', None)
            if keysyms:
                if not isinstance(keysyms, (tuple, list)):
                    keysyms = [keysyms]

                for keysym in keysyms:
                    self.bind(keysym, attr)

    def clear(self):
        self.delete(0, tkinter.END)

    def enter_callback(self, event):
        cmd = self.get()
        self.clear()

        if self.callback:
            self.callback(cmd)
            return

        self.handle_command(cmd)

    @bind_key('c', True)
    def ctrl_c(self, event):
        self.clear()

    @bind_key('d', True)
    def ctrl_d(self, event):
        self.master.quit()

    @bind_key('r', True)
    def ctrl_r(self, event):
        if self.parent.current_app:
            app = self.parent.running_apps[self.parent.current_app]
            app.refresh()

    @bind_key('w', True)
    def ctrl_w(self, event):
        if self.parent.current_app:
            app = self.parent.running_apps[self.parent.current_app]
            app.close_monitor()

    @bind_key(tuple('123456789'), True)
    def ctrl_number(self, event):
        # TODO: Move all this code to a method in `fxi`.
        key = event.keysym
        app = tuple(self.parent.running_apps.values())[int(key) - 1]
        self.parent.notebook.focus_on_app(app)

        for app_name, app_instance in self.parent.running_apps.items():
            if app_instance is app:
                self.parent.current_app = app_name

    def handle_command(self, line):
        commands = re.split(r'; ?', line)
        for command in commands:
            self.do_handle_command(command)

    def do_handle_command(self, command):
        head, *args = re.split(r'\s+', command)

        if not head:
            return

        parsed_args = []
        for arg in args:
            if arg == '!c':
                parsed_args.append(self.master.clipboard_get())
                continue
            parsed_args.append(arg)

        if head[0] == ':':
            head = head[1:]

            try:
                app_name = parsed_args[0]
            except IndexError:
                app_name = self.parent.current_app

            if head == 'q':
                print('Quitting.')
                self.master.quit()
                return

            elif head == 'r':
                app = self.parent.running_apps[app_name]
                importlib.reload(app._module_reference)
                self.parent.unload_app(app_name)
                self.parent.open_app(app_name)
                return

            elif head == 'c':
                self.parent.unload_app(app_name)
                app = tuple(self.parent.running_apps.values())[-1]
                app_name = tuple(self.parent.running_apps.keys())[-1]
                self.parent.notebook.focus_on_app(app)
                self.parent.current_app = app_name
                return

        if head == 'echo':
            print(' '.join(parsed_args))

        if head in self.parent.available_apps:
            t = threading.Thread(target=self.parent.open_app, args=[head])
            t.start()
            return

        if self.parent.current_app:
            app = self.parent.running_apps[self.parent.current_app]
            app.handle_command(head, parsed_args)
            return
