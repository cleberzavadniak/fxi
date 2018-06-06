from io import BytesIO
import tkinter
from tkinter import ttk

from PIL.ImageTk import PhotoImage
from PIL import Image
import requests

from fxi.utils import apply_surrogates


class Slide(ttk.Frame):
    def __init__(self, app, *args, **kwargs):
        self.image_reference = None
        self.text = None
        self.date = None
        self.app = app

        super().__init__(app.tab.interior, *args, **kwargs)

        self.image_slot = ttk.Label(
            self,
            anchor=tkinter.N,
            justify=tkinter.CENTER,
        )
        self.image_slot.pack(expand=True, fill=tkinter.X)

    def set_image_from_url(self, url):
        self.app.enqueue(self.do_set_image_from_url, url)

    def do_set_image_from_url(self, url):
        if not self.app.alive:
            return

        response = requests.get(url)
        if response.status_code != 200:
            print(response.status_code)
            print(response.content)
            return

        image_data = response.content
        image_buffer = BytesIO(image_data)
        image = Image.open(image_buffer)
        width, height = image.size

        max_width = self.master.master.winfo_width() * 0.95
        max_height = self.master.master.winfo_height() * 0.95

        pw = max_width / width
        ph = max_height / height
        p = min(ph, pw)
        if p < 1:
            image.thumbnail((
                int(width * p),
                int(height * p)
            ))

        photoimage = PhotoImage(image)
        self.image_reference = photoimage
        self.image_slot.configure(image=photoimage)

    def render(self):
        if self.text:
            label = ttk.Label(
                self,
                text=apply_surrogates(self.text),
                anchor=tkinter.W,
                justify=tkinter.LEFT
            )
            label.pack(expand=True, fill=tkinter.BOTH)

        if self.date:
            label = ttk.Label(
                self,
                text=apply_surrogates(self.date),
                anchor=tkinter.W,
                justify=tkinter.LEFT
            )
            label.pack(expand=True, fill=tkinter.BOTH)
        self.pack(expand=tkinter.TRUE, fill=tkinter.BOTH)

    def destroy(self):
        self.image_reference = None
        super().destroy()


class ImageSlideShow(ttk.Frame):
    def __init__(self, app, slides, *args, **kwargs):
        self.app = app
        self.tab = app.tab
        self.index = 0
        self.slides = slides

        self.binded_functions = []

    def render(self):
        monitor = self.app.current_monitor
        if isinstance(monitor, ImageSlideShow):
            monitor.close()
            monitor = self.app.current_monitor

        self.previous_monitor = monitor
        self.previous_monitor.pack_forget()
        self.app.current_monitor = self

        self.binded_functions.append(self.app.fxi.command_line.bind("<Left>", self.previous))
        self.binded_functions.append(self.app.fxi.command_line.bind("<Right>", self.next))

        self.refresh()

    @property
    def current_slide(self):
        return self.slides[self.index]

    def clear(self):
        self.current_slide.pack_forget()

    def refresh(self):
        self.current_slide.render()

    def next(self, event=None):
        if self.index + 1 >= len(self.slides):
            return

        self.clear()
        self.index += 1
        self.refresh()

    def previous(self, event=None):
        if self.index - 1 < 0:
            return

        self.clear()
        self.index -= 1
        self.refresh()

    def close(self):
        for fid in self.binded_functions:
            self.tab.unbind_all(fid)

        for slide in self.slides:
            slide.destroy()

        self.app.current_monitor = self.previous_monitor
        self.app.show_current_monitor()
