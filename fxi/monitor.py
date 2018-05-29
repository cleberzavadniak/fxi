from io import BytesIO
import tkinter
from tkinter import ttk

from PIL.ImageTk import PhotoImage
from PIL import Image
import requests


class LazySlot(ttk.Label):
    def write(self, what):
        if isinstance(what, PhotoImage):
            self.write_image(what)
            return

        self.configure(text=what)

    def write_image_from_url(self, url, *args, **kwargs):
        if not self.master.alive:
            return

        response = requests.get(url)
        if response.status_code != 200:
            print(response.status_code)
            print(response.content)
            return

        image_data = response.content
        image_buffer = BytesIO(image_data)
        image = Image.open(image_buffer)
        self.write_image(image, *image.size)
        return image

    def write_image(self, image, width, height):
        max_width = self.master.master.winfo_width() * 0.95

        if width > max_width:
            p = max_width / width
            image.thumbnail((
                int(width * p),
                int(height * p)
            ))
        photoimage = PhotoImage(image)

        label = ttk.Label(
            self,
            image=photoimage,
            anchor=tkinter.N,
            justify=tkinter.CENTER,
        )
        label.pack(expand=True, fill=tkinter.X)
        self.master.lines.append(label)
        self.master.images.append(photoimage)


class MonitorFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.lines = []
        self.images = []
        self.alive = True
        super().__init__(parent, *args, **kwargs)

    def write(self, what, indentation=0):
        if not self.alive:
            return

        if isinstance(what, PhotoImage):
            return self.write_image(what, indentation)

        return self.write_string(what, indentation)

    def write_image_from_url(self, url, *args, **kwargs):
        if not self.alive:
            return

        response = requests.get(url)
        if response.status_code != 200:
            print(response.status_code)
            print(response.content)
            return

        image_data = response.content
        image_buffer = BytesIO(image_data)
        image = Image.open(image_buffer)
        photoimage = PhotoImage(image)
        self.write_image(photoimage, *args, **kwargs)
        return photoimage

    def write_image(self, image, indentation=0):
        width = self.master.winfo_width()
        print('monitor.width:', width)
        label = ttk.Label(
            self,
            image=image,
            anchor=tkinter.W,
            justify=tkinter.CENTER,
            width=width
        )
        label.pack(expand=True, fill=tkinter.X)
        self.lines.append(label)
        self.images.append(image)

    def write_string(self, message, indentation=0):
        if indentation:
            spacer = '-' * (indentation - 1)
            formatted_message = f'+{spacer}{message}'
        else:
            formatted_message = f'{message}'

        width = self.master.master.winfo_width()
        label = ttk.Label(
            self,
            text=formatted_message,
            anchor=tkinter.W,
            justify=tkinter.LEFT,
            wraplength=width
        )
        label.pack(expand=True, fill=tkinter.X)
        self.lines.append(label)
        # self.master.master.master.page_down()  # XXX
        return label

    def add_slot(self, *args, **kwargs):
        slot = LazySlot(self, *args, **kwargs)
        self.lines.append(slot)
        slot.pack(expand=True, fill=tkinter.X)
        return slot

    def hr(self):
        """
        label = ttk.Label(
            self,
            anchor=tkinter.W,
            justify=tkinter.CENTER,
            relief=tkinter.RIDGE
        )
        label.pack(expand=True, fill=tkinter.X, padx=1, pady=1)"""
        separator = ttk.Separator(self)
        separator.pack(fill=tkinter.X, expand=True)

    def header(self, title, style):
        label = ttk.Label(
            self,
            text=f'{title}',
            anchor=tkinter.W,
            justify=tkinter.LEFT,
            style=f'{style}.TLabel'
        )
        label.pack(expand=True, fill=tkinter.X)

    def h1(self, title):
        return self.header(title, 'h1')

    def h2(self, title):
        return self.header(title, 'h2')

    def h3(self, title):
        return self.header(title, 'h3')

    def close(self):
        self.alive = False
        self.images = []
        self.destroy()


class LazyFrameSlot(MonitorFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(relief=tkinter.RIDGE)


class Monitor(MonitorFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent.tab.interior, *args, **kwargs)
        self.frames = []
        self.configure(relief=tkinter.SUNKEN)

    def add_frame_slot(self, *args, **kwargs):
        frame_slot = LazyFrameSlot(self, *args, **kwargs)
        self.frames.append(frame_slot)
        frame_slot.pack(expand=True, fill=tkinter.X)
        return frame_slot
