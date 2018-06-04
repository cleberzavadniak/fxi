from .base import AppBase


class App(AppBase):
    title = 'Main'

    def cmd__ls(self):
        monitor = self.open_monitor('ls')
        for app_name in self.fxi.available_apps:
            monitor.write(app_name)

    def render(self):
        self.h1(self.title)
