from .base import AppBase


class App(AppBase):
    title = 'Main'

    def handle_command(self, command):
        if command == 'ls':
            monitor = self.open_monitor('ls')
            for app_name in self.fxi.available_apps:
                monitor.write(app_name)

    def render(self):
        self.h1(self.title)
