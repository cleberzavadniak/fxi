from tkinter import *
from tkinter.ttk import *


class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.binded_functions = []
        self.alive = True

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(
            self,
            bd=0,
            highlightthickness=0,
            yscrollcommand=vscrollbar.set,
            background='white'
        )
        self.canvas = canvas

        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)
        self.interior_id = interior_id

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        canvas.bind('<Configure>', self._configure_canvas)

        self.bind_scrolling_events()

    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

    def page_down(self):
        self._configure_canvas(None)
        self.canvas.yview_scroll(1, "pages")

    def bind_scrolling_events(self):
        # Scrolling:
        fid = self.bind_all("<Button-4>", self._on_button_4)
        self.binded_functions.append(fid)

        fid = self.bind_all("<Button-5>", self._on_button_5)
        self.binded_functions.append(fid)

        fid = self.bind_all("<Prior>", self._on_page_up)
        self.binded_functions.append(fid)

        fid = self.bind_all("<Next>", self._on_page_down)
        self.binded_functions.append(fid)

    def unbind_scrolling_events(self):
        for fid in self.binded_functions:
            self.unbind_all(fid)

    def destroy(self, *args, **kwargs):
        self.unbind_scrolling_events()
        self.alive = False
        super().destroy(*args, **kwargs)

    def _on_mousewheel(self, event):
        if not self.alive:
            return
        x = int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(x, "units")

    def _on_button_4(self, event):
        if not self.alive:
            return
        self.canvas.yview_scroll(-2, "units")

    def _on_button_5(self, event):
        if not self.alive:
            return
        self.canvas.yview_scroll(2, "units")

    def _on_page_down(self, event):
        if not self.alive:
            return
        self.canvas.yview_scroll(1, "pages")

    def _on_page_up(self, event):
        if not self.alive:
            return
        self.canvas.yview_scroll(-1, "pages")
