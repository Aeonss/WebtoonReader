# Dependencies
import os, json, re
from pathlib import Path
import tkinter as tk 
from tkinter import filedialog
from CustomScroller import ImageScroller

# SETTINGS
SETTINGS_FILE = os.path.join(Path.home(), "webtoonreader_settings.json")


class WebtoonReader:
    def __init__(self):
        
        # Create settings file in the home directory if it does not exist
        if not os.path.isfile(SETTINGS_FILE):
            with open(SETTINGS_FILE, "a") as f:
                json.dump({"width" : 720, "height" : 800, "scroll_speed" : 3, "recent_chapter" : "", "recent_chapter_index" : "", "load" : 5, "invert_drag" : False}, f)
                f.close()
        
        # Checks if paths in settings exists
        else:
            if not os.path.exists(get_json("recent_chapter")):
                update_json("recent_chapter", "")
                update_json("recent_chapter_index", "")
        

        # Window
        self.window = tk.Tk()
        self.window.resizable(False, False)
        
        self.width = get_json('width')
        self.height = get_json('height')
        self.scroll_speed = get_json('scroll_speed')
        self.load = get_json('load')
        self.invert_drag = get_json('invert_drag')
        
        
        # Center Window
        x = int(self.window.winfo_screenwidth()/2 - self.width/2)
        y = int(self.window.winfo_screenheight()/2 - self.height/2)
        self.window.geometry("+{}+{}".format(x, y))
        
        # ImageScroller
        chapter_path = get_json('recent_chapter')
        manga = os.path.basename(os.path.dirname(chapter_path))
        self.frame = ImageScroller(self.window, 
                            path=chapter_path, 
                            scrollbarwidth=15, 
                            width=self.width, 
                            height=self.height, 
                            speed=self.scroll_speed, 
                            load=self.load, 
                            invert=self.invert_drag,
                            manga_name=manga)
        self.frame.pack()
        
        # Menubar
        menubar = tk.Menu(self.window)
        settingsmenu = tk.Menu(menubar, tearoff=0) 
        settingsmenu.add_command(label="Settings", command=self.set_settings)
        settingsmenu.add_command(label="Help")

        # Adding cascade to menubar
        menubar.add_cascade(label="Settings", menu=settingsmenu)
        menubar.add_cascade(label="Load Chapter", command=lambda: self.create_chapter(None))
        menubar.add_cascade(label="Previous Chapter", command=self.prev_chapter)
        menubar.add_cascade(label="Next Chapter", command=self.next_chapter)

        menubar.add_cascade(label="< Top", command=self.scroll_to_start)
        menubar.add_cascade(label="End >", command=self.scroll_to_end)
        menubar.add_cascade(label="Goto", command=self.scroll_to_page)
                
        # Keybind shortcuts for changing chapters
        self.window.bind("<Left>", self.key_prev_chapter)
        self.window.bind("<a>", self.key_prev_chapter)
        self.window.bind("<Right>", self.key_next_chapter)
        self.window.bind("<d>", self.key_next_chapter)

        # Start the window
        self.window.config(menu=menubar)
        self.window.mainloop()
            
    def scroll_to_start(self):
        self.frame.scroll_to_start()

    def scroll_to_end(self):
        self.frame.scroll_to_end()

    def scroll_to_page(self):
        self.frame.scroll_to_page()

    # Loads a chapter to read
    def create_chapter(self, path):
        if path != None:
            chapter_path = path
        else:
            chapter_path = filedialog.askdirectory()
            if chapter_path == "":
                return
        
        
        manga_path = os.path.dirname(chapter_path)
        manga = os.path.basename(manga_path)
        chapter_list = abslistdir(manga_path)
        chapter_index = -1
        
        # Finds the index of the current manga in the directory
        for index, chapter in enumerate(chapter_list):
            if chapter == chapter_path:
                chapter_index = index
                break
        
        # Updates the image scroller
        self.frame.destroy()
        self.frame = ImageScroller(self.window, 
                            path=chapter_path, 
                            scrollbarwidth=15, 
                            width=self.width, 
                            height=self.height, 
                            speed=self.scroll_speed, 
                            load=self.load, 
                            invert=self.invert_drag,
                            manga_name=manga)
        self.frame.pack()
        
        # Updates settings json
        update_json('recent_chapter', chapter_path)
        update_json('recent_chapter_index', chapter_index)
        update_json(manga, chapter_path)


    # Finds the next chapter of the manga
    def next_chapter(self):
        chapter_index = get_json('recent_chapter_index')
        chapter_index += 1
        
        # Checks if the current chapter is the last chapter
        chapter_path = get_json('recent_chapter')
        manga_path = os.path.dirname(chapter_path)
        chapter_list = abslistdir(manga_path)
        
        # Checks if it is the last chapter
        if chapter_index >= len(chapter_list):
            tk.messagebox.showwarning('Warning', 'Last Chapter')
            return
        
        chapter_path = chapter_list[chapter_index]
        
        # Updates the image scroller
        manga = os.path.basename(manga_path)
        self.frame.destroy()
        self.frame = ImageScroller(self.window, 
                            path=chapter_path, 
                            scrollbarwidth=15, 
                            width=self.width, 
                            height=self.height, 
                            speed=self.scroll_speed, 
                            load=self.load, 
                            invert=self.invert_drag,
                            manga_name=manga)
        self.frame.pack()
        
        # Updates the settings json
        update_json('recent_chapter', chapter_path)
        update_json('recent_chapter_index', chapter_index)
        update_json(manga, chapter_path)
    
    
    # Finds the previous chapter of the manga
    def prev_chapter(self):
        chapter_index = get_json('recent_chapter_index')
        chapter_index -= 1
        
        # Checks if the current chapter is the first
        chapter_path = get_json('recent_chapter')
        manga_path = os.path.dirname(chapter_path)
        chapter_list = abslistdir(manga_path)
        
        # Checks if it is the first chapter
        if chapter_index == -1:
            tk.messagebox.showwarning('Warning', 'First Chapter')
            return
        
        chapter_path = chapter_list[chapter_index]
        
        # Updates the image scroller
        manga = os.path.basename(manga_path)
        self.frame.destroy()
        self.frame = ImageScroller(self.window, 
                                   path=chapter_path, 
                                   scrollbarwidth=15, 
                                   width=self.width, 
                                   height=self.height, 
                                   speed=self.scroll_speed, 
                                   load=self.load, 
                                   invert=self.invert_drag,
                                   manga_name=manga)
        self.frame.pack()
        
        # Updates the settings json
        update_json('recent_chapter', chapter_path)
        update_json('recent_chapter_index', chapter_index)
        update_json(manga, chapter_path)
        
        
    # Keybind shortcut for next chapter
    def key_next_chapter(self, e):
        self.next_chapter()
    
    
    # Keybind shortcut for previous chapter
    def key_prev_chapter(self, e):
        self.prev_chapter()


    # Settings window
    def set_settings(self):
        settings = tk.Toplevel()
        x = int(self.window.winfo_screenwidth()/2 - 200)
        y = int(self.window.winfo_screenheight()/2 - 200)
        settings.geometry("%dx%d+%d+%d" % (400, 500, x, y))
        
        width_label = tk.Label(settings, text="Width").pack(pady=10)
        self.width_slider = tk.Scale(settings, from_=200, to=self.window.winfo_screenwidth(), orient=tk.HORIZONTAL, length=300, resolution=20)
        self.width_slider.set(self.width)
        self.width_slider.pack(pady=10)
        self.width_slider.bind("<ButtonRelease-1>", self.update_width)
        
        height_label = tk.Label(settings, text="Height").pack(pady=10)
        self.height_slider = tk.Scale(settings, from_=200, to=self.window.winfo_screenheight(), orient=tk.HORIZONTAL, length=250, resolution=20)
        self.height_slider.set(self.height)
        self.height_slider.pack(pady=10)
        self.height_slider.bind("<ButtonRelease-1>", self.update_height)
        
        speed_label = tk.Label(settings, text="Scroll Speed").pack(pady=10)
        self.scroll_speed_slider = tk.Scale(settings, from_=1, to=5, orient=tk.HORIZONTAL)
        self.scroll_speed_slider.set(self.scroll_speed)
        self.scroll_speed_slider.pack(pady=10)
        self.scroll_speed_slider.bind("<ButtonRelease-1>", self.update_speed)
        
        invert_label = tk.Label(settings, text="Invert Mouse Drag").pack(pady=10)
        self.invert_checkbox = tk.IntVar()
        self.checkbutton = tk.Checkbutton(settings, variable=self.invert_checkbox)
        if self.invert_drag:
            self.checkbutton.select()
        else:
            self.checkbutton.deselect()
        self.checkbutton.pack(pady=10)
        self.checkbutton.bind("<ButtonRelease-1>", self.update_invert)
        
        load_label = tk.Label(settings, text="Number of Images to Load").pack(pady=10)
        self.load_slider = tk.Scale(settings, from_=1, to=20, orient=tk.HORIZONTAL)
        self.load_slider.set(self.load)
        self.load_slider.pack(pady=10)
        self.load_slider.bind("<ButtonRelease-1>", self.update_load)

        settings.mainloop()
    
    
    # Updates width in settings json
    def update_width(self, e):
        self.width = self.width_slider.get()
        update_json('width', self.width)
        self.restart_canvas()
    
    
    # Updates height in settings json
    def update_height(self, e):
        self.height = self.height_slider.get()
        update_json('height', self.height)  
        self.restart_canvas()
        
        
    # Updates scroll speed in settings json
    def update_speed(self, e):
        self.scroll_speed = self.scroll_speed_slider.get()
        update_json('scroll_speed', self.scroll_speed)
        self.restart_canvas()


    # Update invert mouse drag in settings json
    def update_invert(self, e):
        if self.invert_checkbox.get() == 0:
            update_json('invert_drag', True)
            self.invert_drag = True
        else:
            update_json('invert_drag', False)
            self.invert_drag = False
        self.restart_canvas()
    
    # Update number of images to be loaded
    def update_load(self, e):
        self.load = self.load_slider.get()
        update_json('load', self.load)
        self.restart_canvas()
    
    
    def restart_canvas(self):
        manga = os.path.basename(os.path.dirname(chapter_path))
        chapter_path = get_json('recent_chapter')
        self.frame.destroy()
        self.frame = ImageScroller(self.window, 
                                   path=chapter_path, 
                                   scrollbarwidth=15, 
                                   width=self.width, 
                                   height=self.height, 
                                   speed=self.scroll_speed, 
                                   load=self.load, 
                                   invert=self.invert_drag,
                                   manga_name=manga)
        self.frame.pack()




# Update the json value if key exists, otherwise adds to json
def update_json(key, value):
    json_file = open(SETTINGS_FILE, "r")
    data = json.load(json_file)
    data[key] = value
    
    json_file = open(SETTINGS_FILE, "w")
    json_file.write(json.dumps(data))
    json_file.close()
    

# Get json value (with key)
def get_json(key):
    json_file = open(SETTINGS_FILE, "r")
    data = json.load(json_file)
    for item in data:
        if key in item:
            value = data[key]
            json_file.close()
            return value
    json_file.close()
    
    # Recreate the settings file if its broken
    if os.path.isfile(SETTINGS_FILE):
        os.remove(SETTINGS_FILE)
        with open(SETTINGS_FILE, "a") as f:
            json.dump({"width" : 720, "height" : 800, "scroll_speed" : 3, "recent_chapter" : "", "recent_chapter_index" : "", "load" : 5, "invert_drag" : False}, f)
            f.close()
    return get_json(key)


# Returns a natural sorted list of absolute paths directories
def abslistdir(path):
    list = []
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            list.append(os.path.join(root, dir).replace("\\", "/"))
    list.sort(key=natural_sort)
    return list


# Natural sort a list
def natural_sort(list):
    return [int(text) if text.isdigit() else text.lower()
        for text in re.split(re.compile('([0-9]+)'), list)]  



# Main
if __name__ == "__main__":
    WebtoonReader()