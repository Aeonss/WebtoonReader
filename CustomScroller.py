# Referenced from: https://stackoverflow.com/a/56046307

import tkinter as tk
import os, re, math
from PIL import ImageTk, Image
from tkinter import simpledialog

# Custom infinite seamless vertical image scroller using Tkinter Canvas and Scrollbar
class ImageScroller(tk.Frame):
    def __init__(self, master=None, **kw):

        # Initialization
        self.window = master
        self.manga_name = kw.pop('manga_name', '')
        self.path = kw.pop('path', None)
        self.width = kw.pop('width', None)
        self.height = kw.pop('height', None)
        self.bg = kw.pop('bg', None)
        self.scroll_speed = kw.pop('speed', None)
        self.image_load = kw.pop('load', None)
        self.invert = kw.pop('invert', None)
        sw = kw.pop('scrollbarwidth', 10)
        super(ImageScroller, self).__init__(master=master, **kw)
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg=self.bg, highlightthickness=0, **kw)

        # List of images
        self.images = []

        self.scroll_flag = True
        self.image_index = 0
        self.top = self.canvas.yview()[1]

        # Fill the frame with images if there is a chapter to load
        if self.path != "":
            self.fill(self.image_index)

        # Create vertical scrollbar
        self.v_scroll = tk.Scrollbar(self, orient='vertical', width=sw)

        # Grid and configure weight
        self.canvas.grid(row=0, column=0,  sticky='nsew')
        self.v_scroll.grid(row=0, column=1, sticky='ns')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Set the scrollbars to the canvas
        self.canvas.config(yscrollcommand=self.v_scroll.set)

        # Set canvas view to the scrollbars
        self.v_scroll.config(command=self.canvas.yview)

        # Scroll to go through canvas
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        self.canvas.bind_class(self.canvas, "<MouseWheel>", self.mouse_scroll)
        self.canvas.bind("<Button-4>", self.mouse_scroll)
        self.canvas.bind("<Button-5>", self.mouse_scroll)

        # Click to drag through canvas
        self.canvas.bind("<Button-1>", self.start_scroll)
        self.canvas.bind("<B1-Motion>", self.update_scroll)
        self.canvas.bind("<ButtonRelease-1>", self.stop_scroll)

        # Set window name
        self.update_title_name()

    # Mouse scroll handling
    def mouse_scroll(self, event):
        # Linux uses event.num
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(self.scroll_speed * -1, "units" )

        # Windows / Mac
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(self.scroll_speed, "units" )

        self.checkLoadChapter()


    def key_scroll(self, scroll=1, type="units"):
        scroll_value = scroll

        # Scale arrow scroll with scroll speed from settings
        if type == "units":
            scroll_value = scroll * self.scroll_speed

        self.canvas.yview_scroll(scroll_value, type)


    # Mouse drag handling
    # https://shortrecipes.blogspot.com/2014/05/python-3-and-tkinter-scroll-canvas-with.html
    def start_scroll(self, event):
        self.canvas.config(yscrollincrement=3)
        self.canvas.config(xscrollincrement=3)
        self._starting_drag_position = (event.x, event.y)

        # https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/cursors.html
        self.canvas.config(cursor="hand2")


    def update_scroll(self, event):
        deltaX = event.x - self._starting_drag_position[0]
        deltaY = event.y - self._starting_drag_position[1]
        self.canvas.xview('scroll', deltaX, 'units')

        if self.invert:
            self.canvas.yview('scroll', -deltaY, 'units')
        else:
            self.canvas.yview('scroll', deltaY, 'units')
        self._starting_drag_position =  (event.x, event.y)

        self.checkLoadChapter()

    def stop_scroll(self, event):
        self.canvas.config(xscrollincrement=0)
        self.canvas.config(yscrollincrement=0)
        self.canvas.config(cursor="")

    def scroll_to_start(self):
        self.canvas.yview_moveto(0.01)

    def scroll_to_end(self):
        self.canvas.yview_moveto(0.99)

    # Load page from popup input
    def scroll_to_page(self):
        total_size = len(os.listdir(self.path))
        current_page = math.floor(self.image_index / self.image_load) + 1
        total_pages = math.ceil(max(1, total_size / self.image_load))
        goto_page = simpledialog.askinteger("Go to page",
                                f"Go to page (1 - {total_pages})", initialvalue=current_page, minvalue=1, maxvalue=total_pages)

        # Don't process if cancel or same page
        if goto_page != None and current_page != goto_page:
            self.image_index = (goto_page-1) * self.image_load
            self.fill(self.image_index)
            self.scroll_flag = False
            self.v_scroll.config(command=self.canvas.yview)
            self.canvas.config(scrollregion=self.canvas.bbox('all'))

            self.canvas.yview_moveto(0)
            self.top = self.canvas.yview()[1]

            self.update_title_name()

    # Fills the frame with images from the folder path
    def fill(self, index):

        self.window.title(f"Loading...")
        # Free memory from previous load
        self.canvas.delete('all')
        self.images.clear()

        for i in range(self.image_load):
            if index + i >= len(os.listdir(self.path)):
                break

            img = Image.open(os.path.join(self.path, self.natural_sort(os.listdir(self.path))[index + i]))

            # Rescales all images to width
            if img.width != self.width:
                scale = img.height / img.width
                img = img.resize((self.width, int(self.width * scale)), Image.Resampling.LANCZOS)

            # Adds to list to prevent garbage collection
            self.images.append(ImageTk.PhotoImage(img))

        height = 0

        for i in range(len(self.images)):
            self.canvas.create_image(0, height, anchor=tk.NW, image=self.images[i])
            height = height + self.images[i].height()



    def checkLoadChapter(self):
        # If at the top of the scrollbar, load previous images
        if self.v_scroll.get()[1] == self.top:
            if self.scroll_flag and self.image_index - self.image_load >= 0:
                self.image_index -= self.image_load
                self.fill(self.image_index)
                self.scroll_flag = False
                self.v_scroll.config(command=self.canvas.yview)
                self.canvas.config(scrollregion=self.canvas.bbox('all'))
                self.canvas.yview_moveto(1)
                self.update_title_name()

        # If at the bottom of the scrollbar, load next images
        if self.v_scroll.get()[1] == 1:
            if self.scroll_flag and self.image_index + self.image_load < len(os.listdir(self.path)):
                self.image_index += self.image_load
                self.fill(self.image_index)
                self.scroll_flag = False
                self.v_scroll.config(command=self.canvas.yview)
                self.canvas.config(scrollregion=self.canvas.bbox('all'))
                self.canvas.yview_moveto(0)
                self.top = self.canvas.yview()[1]
                self.update_title_name()



        # Enable flag to load next images
        if self.v_scroll.get()[1] > self.top and self.v_scroll.get()[1] != 1:
            self.scroll_flag = True

    def update_title_name(self):
        if self.path == '':
            self.window.title("WebtoonReader")
            return

        total_size = len(os.listdir(self.path))
        current_page = math.floor(self.image_index / self.image_load) + 1
        total_pages = math.ceil(max(1, total_size / self.image_load))
        self.window.title(f"[WebtoonReader] - {self.manga_name} : {os.path.basename(self.path)} | Page ({current_page} / {total_pages})")

    # Natural sort files
    def natural_sort(self, l):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(l, key=alphanum_key)