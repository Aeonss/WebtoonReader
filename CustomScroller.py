# Referenced from: https://stackoverflow.com/a/56046307

import tkinter as tk
import os, re
from PIL import ImageTk, Image

# Custom infinite seamless vertical image scroller using Tkinter Canvas and Scrollbar
class ImageScroller(tk.Frame):
    def __init__(self, master=None, **kw):
        
        # Initialization
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

    # Mouse scroll handling
    def mouse_scroll(self, event):
        # Linux uses event.num
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(self.scroll_speed * -1, "units" )
            
        # Windows / Mac
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(self.scroll_speed, "units" )
        
        self.checkLoadChapter()
                
            
            
            
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
        
    # Fills the frame with images from the folder path
    def fill(self, index):

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
                
                
                        
        # Enable flag to load next images
        if self.v_scroll.get()[1] > self.top and self.v_scroll.get()[1] != 1:
            self.scroll_flag = True


    # Natural sort files
    def natural_sort(self, l): 
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(l, key=alphanum_key)