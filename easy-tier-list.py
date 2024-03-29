"""
  ______           _______     __  _______ _____ ______ _____        _      _____  _____ _______ 
 |  ____|   /\    / ____\ \   / / |__   __|_   _|  ____|  __ \      | |    |_   _|/ ____|__   __|
 | |__     /  \  | (___  \ \_/ /_____| |    | | | |__  | |__) |_____| |      | | | (___    | |   
 |  __|   / /\ \  \___ \  \   /______| |    | | |  __| |  _  /______| |      | |  \___ \   | |   
 | |____ / ____ \ ____) |  | |       | |   _| |_| |____| | \ \      | |____ _| |_ ____) |  | |   
 |______/_/    \_\_____/   |_|       |_|  |_____|______|_|  \_\     |______|_____|_____/   |_|

 Author: Akash Bora (Akascape)
 License: MIT
 Version: 1.1
"""

import customtkinter
import tkinter
from PIL import Image, ImageTk, ImageGrab
from CTkMenuBar import *
from tkinter import filedialog
from CTkColorPicker import *
from CTkMessagebox import *
from tkinterdnd2 import TkinterDnD, DND_ALL
import os
from urllib.request import urlopen
import io
import json
import shutil
import random
import sys

platform = sys.platform
if platform.startswith("win"):
    import pywinstyles
    
customtkinter.set_appearance_mode("Dark") 
customtkinter.set_default_color_theme("blue")
customtkinter.set_widget_scaling(1.0)
customtkinter.set_window_scaling(1.0)
customtkinter.deactivate_automatic_dpi_awareness()

class CTk(customtkinter.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)
        
class App(CTk):
    
    def __init__(self):
        
        super().__init__()
        self.geometry("1000x800")
        self.title("Easy-Tier-List")
        
        self.icopath = ImageTk.PhotoImage(file=self.resource("logo.png"))
        self.wm_iconbitmap()
        self.iconphoto(False, self.icopath)
        self.bind("<ButtonRelease-1>", lambda event: event.widget.focus_set() if type(event.widget) is not str else None, add="+")
        self.protocol("WM_DELETE_WINDOW", self.ask_leave)
        
        menu = CTkMenuBar(self)
        button_1 = menu.add_cascade("File")
        button_2 = menu.add_cascade("Add Category", command=self.new_category)
        button_3 = menu.add_cascade("Add Content", command=self.edit_content)
        button_4 = menu.add_cascade("Settings")

        dropdown1 = CustomDropdownMenu(widget=button_1, corner_radius=4, width=100)
        dropdown1.add_option(option="Open", command=self.open_template)
        
        self.submenu = dropdown1.add_submenu("Save")
        self.submenu.add_option(option="JSON", command=self.save_template)
        self.submenu.add_option(option="JSON+Images", command=lambda: self.save_template(copy=True))
        self.submenu.add_option(option="Screenshot", command=self.export_image)

        dropdown2 = CustomDropdownMenu(widget=button_4, corner_radius=4, width=100)
        dropdown2.add_option(option="Adjust Font", command=self.adjust_font)
        dropdown2.add_option(option="Adjust Theme", command=self.adjust_theme)
        dropdown2.add_option(option="Toggle Fullscreen", command=self.toggle_fullscreen)
        dropdown2.add_option(option="About", command=self.show_about)
        
        self.bg_frame = customtkinter.CTkFrame(self)
        self.bg_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.frame_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["top_fg_color"])
        self.frame_color2 = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"])

        self.theme_colors = {"bg":self.frame_color2, "fg":self.frame_color, "txt":"black"}
        
        self.font_data = {"family":"default", "size":15, "weight":0, "slant":0, "underline":0}
        self.global_font = customtkinter.CTkFont()
        
        self.blocks = {"S":{"fg":"#fe7e7e","content":[]}, "A":{"fg":"#ffbf7f","content":[]},
                       "B": {"fg":"#ffdf7f","content":[]}, "C":{"fg":"#ffff7f","content":[]},
                       "D":{"fg":"#bfff7f","content":[]}, "E":{"fg":"#7fff7f","content":[]}, "ALL":{"content":[]}}
        
        self.frame_data = []
        
        for i in self.blocks:
            if i!="ALL":
                self.make_category(i, self.blocks[i]["fg"])
                
        self.update_global_font()
        
        self.content_frame = customtkinter.CTkScrollableFrame(self, height=150, orientation="horizontal",
                                                              label_text="TIERLIST")
        self.content_frame.pack(padx=10, pady=(0,10), fill="both")
        
        self.blocks["ALL"].update({"frame":self.content_frame})
        
        self.drop_target_register(DND_ALL)
        self.dnd_bind("<<Drop>>", self.dropped_content)
        
        self.fullscreen = False

        self.bind("<Escape>", lambda e: self.disable_fullscreen())
        self.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.bind("<n>", lambda e: self.new_category())
        self.bind("<f>", lambda e: self.adjust_font())
        self.bind("<Control-s>", lambda e: self.save_template())
        self.bind("<Control-o>", lambda e: self.open_template())
        self.bind("<t>", lambda e: self.adjust_theme())
        self.bind("<space>", lambda e: self.edit_content())
        
    def toggle_fullscreen(self):
        if not self.fullscreen:
            self.wm_attributes("-fullscreen", 1)
            self.fullscreen = True
        else:
            self.wm_attributes("-fullscreen", 0)
            self.fullscreen = False
        self.resizable(True, True)
        
    def disable_fullscreen(self):
        if self.fullscreen:
            self.wm_attributes("-fullscreen", 0)
            self.fullscreen = False
            self.resizable(True, True)
            
    def ask_leave(self):
        res = CTkMessagebox(self, title="Exit?", message="Do you want to close the program?",
                            option_1="Cancel", option_2="No", option_3="Yes", icon="question")
        if res.get()=="Yes":
            self.destroy()
            
    def resource(self, relative_path):
        base_path = getattr(
            sys,
            '_MEIPASS',
            os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    
    def show_about(self):
        CTkMessagebox(self, title="About", message="Easy-Tier-List \nAuthor: Akash Bora (Akascape) \nVersion: 1.1 \nLicense: MIT",
                      icon=self.resource("logo.png"))
        
    def open_template(self, saved_data=False):
        if not saved_data:
            saved_data = {}
            for i in self.blocks:
                saved_data[i] = self.blocks[i]
   
            open_json = tkinter.filedialog.askopenfilename(filetypes=[('json', ['*.json']),('All Files', '*.*')])
            if open_json:
                with open(open_json) as f:
                    self.blocks = json.load(f)
            else:
                return
        else:
            self.blocks = saved_data
            
        asset_folder = None
        
        if "DATAPATH" in self.blocks:
            asset_folder = os.path.join(os.path.dirname(open_json), self.blocks["DATAPATH"])
            del self.blocks["DATAPATH"]
            if not os.path.exists(asset_folder):
                CTkMessagebox(self, title="No Assets", message="This tierlist is missing the assets folder!", icon="cancel")

        self.font_data = {"family":"default", "size":15, "weight":0, "slant":0, "underline":0}
        
        if "font" in self.blocks:
            self.font_data = self.blocks["font"]
            del self.blocks["font"]
        self.update_global_font()


        self.frame_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["top_fg_color"])
    
        self.theme_colors = {"bg":self.frame_color2, "fg":self.frame_color, "txt":"black"}
        
        if "theme" in self.blocks:
            self.theme_colors = self.blocks["theme"]
            del self.blocks["theme"]
        
        for i in self.frame_data:
            i.destroy()
        self.frame_data = []

        try:
            for i in self.blocks:
                if i!="ALL":
                    self.make_category(i, self.blocks[i]["fg"])
        
            self.blocks["ALL"].update({"frame":self.content_frame})
            
            for i in self.content_frame.winfo_children():
                i.destroy()
     
            for i in self.blocks:
                frame = self.blocks[i]["frame"]
                img_list = self.blocks[i]["content"]
                new_list = []
                for j in img_list:
                    if asset_folder:
                        j = os.path.join(asset_folder, j)
                    new_list.append(j)
                    self.new_content(j, frame=frame)
                self.blocks[i]["content"] = new_list
            saved_data = {}
            self.update_colors()
            self.content_frame.configure(label_text=os.path.basename(open_json).split(".")[0])
        except Exception as errors:
            self.blocks = {"ALL":{"content":[]}}
            CTkMessagebox(self, title="Invalid File", message="This file is not compatible!", icon="cancel")
            self.open_template(saved_data)
    
    def update_global_font(self):
        if self.font_data["family"]!="default":
            self.global_font.configure(family=self.font_data["family"])
        else:
            self.global_font.configure(family=customtkinter.ThemeManager.theme["CTkFont"]["family"])
 
        self.global_font.configure(size=self.font_data["size"])
            
        if self.font_data["underline"]:
            self.global_font.configure(underline=1)
        else:
            self.global_font.configure(underline=0)
        if self.font_data["slant"]:
            self.global_font.configure(slant="italic")
        else:
            self.global_font.configure(slant="roman")
        if self.font_data["weight"]:
            self.global_font.configure(weight="bold")
        else:
            self.global_font.configure(weight="normal")
            
    def save_template(self, copy=False):
        
        template_data = {}

        for i in self.blocks:
            if i=="ALL":
                template_data.update({i:{"content":self.blocks[i]["content"]}})
            else:
                template_data.update({i:{"fg":self.blocks[i]["fg"], "content":self.blocks[i]["content"]}})
                
        template_data.update({"font":self.font_data})
        template_data.update({"theme":self.theme_colors})
        
        save_file = filedialog.asksaveasfilename(initialfile="", defaultextension=".json",
                                                 filetypes=[('json', ['*.json']),('All Files', '*.*')])
        
        if not save_file:
            return
        
        if copy:
            new_list = []
            for i in template_data:
                img_list = template_data[i]["content"]
                for j in img_list:
                    new_list.append(os.path.basename(j))
                template_data[i]["content"] = new_list
                new_list = []
                
            folder = os.path.join(os.path.dirname(save_file),f"{os.path.basename(save_file).split('.')[0]}_assets")
            template_data.update({"DATAPATH":os.path.basename(folder)})
            if not os.path.exists(folder):
                os.mkdir(folder)
            try:
                self.copy_images(folder)
            except:
                CTkMessagebox(self, title="Permission Error!", message="Cannot copy the images, can be a permission error.",
                              icon="cancel")
            
                
        with open(save_file, "w") as f:
            json.dump(template_data, f, indent=2)
            f.close()

        self.content_frame.configure(label_text=os.path.basename(save_file).split(".")[0])
        CTkMessagebox(self, title="Done!", message=f"Data Exported Successfully: \n{save_file}", icon="check")

    def copy_images(self, folder):
        for i in self.blocks:
            for j in self.blocks[i]["content"]:
                dest = os.path.join(folder, os.path.basename(j))
                if (os.path.exists(j)) and not (os.path.exists(dest)):
                    shutil.copy(j, folder)
                        
    def export_image(self):
        save_file = filedialog.asksaveasfilename(initialfile="untitled", defaultextension=".png",
                                                 filetypes=[("Images", ["*.png", "*.jpg", "*.jpeg"]),
                                                            ("All Files", "*.*")])
        if save_file:
            points = (self.bg_frame.winfo_rootx(), self.bg_frame.winfo_rooty(),
                      self.bg_frame.winfo_rootx()+self.bg_frame.winfo_width(),
                      self.bg_frame.winfo_rooty()+self.bg_frame.winfo_height())
            ImageGrab.grab().crop(points).save(save_file)
            
            CTkMessagebox(self, title="Done!", message=f"Image Exported Successfully: \n{save_file}", icon="check")
        
    def dropped_content(self, event):
        dropped_file = event.data.split("{")
        files = []
        for i in dropped_file:
            i = i.replace("{","").replace("} ","").replace("}","")
            if os.path.isfile(i):
                files.append(i)

        for i in files:
            self.new_content(i)
                
    def edit_content(self):
        def remove(path, frame):
            content.remove(path)
            frame.destroy()
            
        def add_image(open_files=None):
            if open_files is None:
                open_files = filedialog.askopenfilenames(filetypes=[("Images", ["*.png", "*.jpg", "*.jpeg"]),
                                                                    ("All Files", "*.*")])
            
            if open_files:
                for file in open_files:
                    try:
                        img = customtkinter.CTkImage(Image.open(file))
                    except:
                        return
                    for i in self.blocks:
                        img_list = self.blocks[i]["content"]
                        if file in img_list:
                            CTkMessagebox(self, title="Duplicate!", message="This image is already imported.", icon="warning")
                            return
                        
                    base = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
                    base.pack(pady=(0,5), fill="x", expand=True)
                    
                    delete_button = customtkinter.CTkButton(base, width=30, text="✕", fg_color="transparent", border_width=1,
                                                            command=lambda path=file, frame=base: remove(path, frame))
                    delete_button.pack(side="left", padx=(0,5))
                    
                    button = customtkinter.CTkButton(base, text=os.path.basename(file), image=img, compound="bottom",
                                                     fg_color="transparent", border_width=1)
                    button.pack(side="left", fill="x", expand=True)

                    content.append(file)
                    
        def add_url():
            get_url = customtkinter.CTkInputDialog(text="Paste Image URL", title="Paste Link")
            self.after(200, lambda: get_url.iconphoto(False, self.icopath))
            url = get_url.get_input()
            if url:
                try:
                    file = urlopen(url)
                    raw_data = file.read()
                    file.close()
                    image = Image.open(io.BytesIO(raw_data))
                except:
                    CTkMessagebox(self, title="Error...", message="Error while retrieving the data! \nCheck the image link and your internet connection.",
                                  icon="warning")
                    return
                
                for i in self.blocks:
                    img_list = self.blocks[i]["content"]
                    if url in img_list:
                        CTkMessagebox(self, title="Duplicate!", message="This image is already imported.", icon="warning")
                        return
                    
                base = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
                base.pack(pady=(0,5), fill="x", expand=True)
                    
                delete_button = customtkinter.CTkButton(base, width=30, text="✕", fg_color="transparent", border_width=1,
                                                            command=lambda path=url, frame=base: remove(path, frame))
                delete_button.pack(side="left", padx=(0,5))
                    
                button = customtkinter.CTkButton(base, text=url, image=customtkinter.CTkImage(image), compound="bottom",
                                                     fg_color="transparent", border_width=1)
                button.pack(side="left", fill="x", expand=True)

                content.append(url)
                    
        def save():
            for i in content:
                self.new_content(i)
            toplevel.destroy()

        content = []
        toplevel = customtkinter.CTkToplevel(self)
        toplevel.resizable(False, False)
        toplevel.transient(self)
        toplevel.title("Add Content")
        
        self.after(200, lambda: toplevel.iconphoto(False, self.icopath))
        
        frame = customtkinter.CTkFrame(toplevel, fg_color="transparent")
        frame.pack(pady=5, padx=5)
        
        image_button = customtkinter.CTkButton(frame, text="Add Images", command=add_image)
        image_button.pack(padx=5, fill="x", side="left")

        url_button = customtkinter.CTkButton(frame, text="Add URL Image", command=add_url)
        url_button.pack(padx=(0,5), fill="x", side="right")
        
        scroll_frame = customtkinter.CTkScrollableFrame(toplevel)
        scroll_frame.pack(expand=True, fill="both")

        save_button = customtkinter.CTkButton(toplevel, text="IMPORT", command=save)
        save_button.pack(padx=10, fill="x", pady=5)
        
        spawn_x = int(self.winfo_width() * .5 + self.winfo_x() - .5 * 300 + 7)
        spawn_y = int(self.winfo_height() * .5 + self.winfo_y() - .5 * toplevel.winfo_height() + 20)
        
        toplevel.geometry(f"+{spawn_x}+{spawn_y}")
        toplevel.grab_set()
        
    def new_category(self, frame=None):
        def add_category():
            if (len(entry_.get())>0) and entry_.get()!="ALL":
                if not frame:
                    self.blocks.update({entry_.get():{"fg":color.cget("fg_color"), "content":[]}})
                    self.make_category(entry_.get(), color.cget("fg_color"))
                else:
                    self.blocks[frame.cget("text")].update({"fg":color.cget("fg_color")})
                    new_dict = {}
                    for key, value in self.blocks.items():
                        if key==frame.cget("text"):
                            new_dict[entry_.get()] = value
                        else:
                            new_dict[key] = value
                    self.blocks = new_dict
                    frame.configure(text=entry_.get(), fg_color=color.cget("fg_color"))
                                
                toplevel.destroy()
            else:
                entry_.configure(placeholder_text_color="#fe7e7e", text_color="#fe7e7e")
                self.after(1000, lambda: entry_.configure(text_color=["black","white"]))
                
        def change_color():
            color_box = AskColor(title=f"Choose Category Color")
            self.after(200, lambda: color_box.iconphoto(False, self.icopath))
            new_color = color_box.get()
            if new_color:
                color.configure(fg_color=new_color)
                
        toplevel = customtkinter.CTkToplevel(self)
        toplevel.resizable(False, False)
        toplevel.transient(self)
        
        toplevel.title("Add New Category")
        self.after(200, lambda: toplevel.iconphoto(False, self.icopath))
        
        entry_ = customtkinter.CTkEntry(toplevel, placeholder_text="Category Name", width=300)
        entry_.pack(fill="x", padx=5, pady=10)
        
        random_color = "#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])

        color = customtkinter.CTkButton(toplevel, text="Color", hover=False, border_width=2,
                                        fg_color=random_color, command=change_color)
        color.pack(fill="x", padx=5, pady=(0,10))

        ok = customtkinter.CTkButton(toplevel, text="OK", command=add_category)
        ok.pack(fill="x", padx=5, pady=(0,10))
        
        spawn_x = int(self.winfo_width() * .5 + self.winfo_x() - .5 * 300 + 7)
        spawn_y = int(self.winfo_height() * .5 + self.winfo_y() - .5 * toplevel.winfo_height() + 20)
        toplevel.geometry(f"+{spawn_x}+{spawn_y}")

        if frame:
            entry_.insert(0, frame.cget("text"))
            color.configure(fg_color=frame.cget("fg_color"))
            toplevel.title("Edit Category")

        toplevel.grab_set()

    def adjust_font(self):

        def change_size(val):
            self.global_font.configure(size=int(val))

        def change_font_family(val):
            self.global_font.configure(family=val)
            if val=="default":
                self.global_font.configure(family=customtkinter.ThemeManager.theme["CTkFont"]["family"])
                
        def toggle_bold():
            if bold_box.get():
                self.global_font.configure(weight="bold")
            else:
                self.global_font.configure(weight="normal")

        def toggle_slant():
            if italic_box.get():
                self.global_font.configure(slant="italic")
            else:
                self.global_font.configure(slant="roman")

        def toggle_underline():
            if underline_box.get():
                self.global_font.configure(underline=1)
            else:
                self.global_font.configure(underline=0)

        def save():
            if bold_box.get():
                self.font_data.update({"weight":1})
            if italic_box.get():
                self.font_data.update({"slant":1})
            if underline_box.get():
                self.font_data.update({"underline":1})
            if font_box.get()!="default":
                self.font_data.update({"family":font_box.get()})
                self.global_font.configure(family=font_box.get())
            if int(size_slider.get())!=15:
                self.font_data.update({"size":int(size_slider.get())})
            toplevel.destroy()
            
        toplevel = customtkinter.CTkToplevel(self)
        toplevel.resizable(False, False)
        toplevel.transient(self)
        toplevel.protocol("WM_DELETE_WINDOW", save)
        
        toplevel.title("Adjust Font and Size")
        self.after(200, lambda: toplevel.iconphoto(False, self.icopath))

        customtkinter.CTkLabel(toplevel, text="Text Font").pack(anchor="w", padx=12)
        font = customtkinter.CTkFont(family="", size=10, )
        
        font_values = ["default"] + list(tkinter.font.families())
        
        font_box = customtkinter.CTkComboBox(toplevel, width=200, values=font_values, command=change_font_family)
        font_box.pack(expand=True, fill="x", padx=10, pady=5)
        font_box.set(self.font_data["family"])
        
        label_ = customtkinter.CTkLabel(toplevel, text="Font Size")
        label_.pack(anchor="w", padx=12)
        
        size_slider = customtkinter.CTkSlider(toplevel, from_=10, to=35, number_of_steps=10, command=change_size)
        size_slider.pack(expand=True, fill="x", padx=8)
        size_slider.set(self.font_data["size"])
        
        frame = customtkinter.CTkFrame(toplevel, fg_color="transparent")
        frame.pack(pady=10, padx=(15,0))
        
        bold_box = customtkinter.CTkCheckBox(frame, text="Bold", command=toggle_bold)
        bold_box.pack(side="left")

        if self.font_data["weight"]:
            bold_box.select()
    
        italic_box = customtkinter.CTkCheckBox(frame, text="Italic", command=toggle_slant)
        italic_box.pack(side="left")

        if self.font_data["slant"]:
            italic_box.select()
                       
        underline_box = customtkinter.CTkCheckBox(frame, text="Underline", command=toggle_underline)
        underline_box.pack(side="left")
        
        if self.font_data["underline"]:
            underline_box.select()
                       
        ok = customtkinter.CTkButton(toplevel, text="OK", command=save)
        ok.pack(expand=True, fill="x", side="bottom", padx=10, pady=(0,10))
        
        spawn_x = int(self.winfo_width() * .5 + self.winfo_x() - .5 * 300 + 7)
        spawn_y = int(self.winfo_height() * .5 + self.winfo_y() - .5 * toplevel.winfo_height() + 20)
        toplevel.geometry(f"+{spawn_x}+{spawn_y}")

        toplevel.grab_set()

    def update_colors(self):
        for i in self.frame_data:
            i.configure(fg_color=self.theme_colors["fg"])
            for j in i.winfo_children():
                if type(j) is tkinter.Label:
                     j.configure(bg=self.theme_colors["fg"])
                elif type(j) is customtkinter.CTkButton:
                    j.configure(text_color=self.theme_colors["txt"])
                    
        self.bg_frame.configure(fg_color=self.theme_colors["bg"])
        
    def adjust_theme(self):

        def change_fg():
            color_box = AskColor(title=f"Choose FG Color")
            self.after(200, lambda: color_box.iconphoto(False, self.icopath))
            new_color = color_box.get()
            if not new_color:
                new_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["top_fg_color"])
                
            self.theme_colors.update({"fg":new_color})
            self.frame_color = new_color
            bt1.configure(fg_color=new_color)
            self.update_colors()
                
        def change_bg():
            color_box = AskColor(title=f"Choose BG Color")
            self.after(200, lambda: color_box.iconphoto(False, self.icopath))
            new_color = color_box.get()
            if not new_color:
                new_color = self.frame_color2
                
            self.theme_colors.update({"bg":new_color})
            bt2.configure(fg_color=new_color)
            self.update_colors()
            
        def change_txt():
            color_box = AskColor(title=f"Choose Text Color")
            self.after(200, lambda: color_box.iconphoto(False, self.icopath))
            new_color = color_box.get()
            if not new_color:
                new_color = "black"
                
            self.theme_colors.update({"txt":new_color})
            bt3.configure(fg_color=new_color)
            self.update_colors()
                
        toplevel = customtkinter.CTkToplevel(self)
        toplevel.resizable(False, False)
        toplevel.transient(self)
        
        toplevel.title("Adjust Colors")
        self.after(200, lambda: toplevel.iconphoto(False, self.icopath))
        
        frame1 = customtkinter.CTkFrame(toplevel, fg_color="transparent")
        frame1.pack(expand=True, fill="x", padx=10, pady=5)

        customtkinter.CTkLabel(frame1, width=100, anchor="w", text="FG Color").pack(side="left", padx=(0,10))
        bt1 = customtkinter.CTkButton(frame1, text="", hover=False, fg_color=self.theme_colors["fg"],
                                      width=30, border_width=2, command=change_fg)
        bt1.pack(side="right")

        frame2 = customtkinter.CTkFrame(toplevel, fg_color="transparent")
        frame2.pack(expand=True, fill="x", padx=10, pady=5)

        customtkinter.CTkLabel(frame2, text="BG Color").pack(side="left", padx=(0,10))
        bt2 = customtkinter.CTkButton(frame2, text="", hover=False, fg_color=self.theme_colors["bg"],
                                      width=30, border_width=2, command=change_bg)
        bt2.pack(side="right")

        frame3 = customtkinter.CTkFrame(toplevel, fg_color="transparent")
        frame3.pack(expand=True, fill="x", padx=10, pady=5)

        customtkinter.CTkLabel(frame3, text="Text Color").pack(side="left", padx=(0,10))
        bt3 = customtkinter.CTkButton(frame3, text="", hover=False, fg_color=self.theme_colors["txt"],
                                      width=30, border_width=2, command=change_txt)
        bt3.pack(side="right")
        
        spawn_x = int(self.winfo_width() * .5 + self.winfo_x() - .5 * 300 + 7)
        spawn_y = int(self.winfo_height() * .5 + self.winfo_y() - .5 * toplevel.winfo_height() + 20)
        toplevel.geometry(f"+{spawn_x}+{spawn_y}")

        toplevel.grab_set()
        
    def make_category(self, text, color):

        frame = customtkinter.CTkFrame(self.bg_frame, fg_color=self.frame_color)
        frame.pack(expand=True, fill="both", pady=5)

        button = customtkinter.CTkButton(frame, width=100, text_color="black", font=self.global_font,
                                        text=text, fg_color=color, hover=False)
        button.pack(fill="y", side="left")
        button._text_label.config(wraplength=90)
        
        self.frame_data.append(frame)

        self.blocks[text].update({"frame":frame})
        
        menu = tkinter.Menu(button, tearoff=False, background=self.frame_color, fg='white', borderwidth=0, bd=0)
            
        menu.add_command(label="Delete Category", command=lambda frame=frame: self.clear_list(frame, delete=True))
        menu.add_command(label="Clear List", command=lambda frame=frame: self.clear_list(frame))
        menu.add_command(label="Move Up", command=lambda frame=frame: self.move(frame, "up"))
        menu.add_command(label="Move Down", command=lambda frame=frame: self.move(frame, "down"))
        menu.add_command(label="Configure", command=lambda frame=button: self.new_category(frame))
            
        button.bind("<Button-3>", lambda event, frame=menu: self.do_popup(event, frame=frame))
        button.bind("<Button-2>", lambda event, frame=menu: self.do_popup(event, frame=frame))
        return frame

    def clear_list(self, frame, delete=False):
        if delete:
            if len(frame.winfo_children())>1:
                ask = CTkMessagebox(self, title="Delete?", message="Delete this category? \n(Process not reversible)",
                                    option_1="No", option_2="Yes", icon="question")
                if ask.get()!="Yes":
                    return
            
        content = []
        for i in self.blocks:
            if self.blocks[i]["frame"]==frame:
                 content = self.blocks[i]["content"]
                 self.blocks[i]["content"] = []
        
        for i in content:
            self.new_content(i, frame=self.content_frame)
      
        for i in frame.winfo_children():
            if type(i) is tkinter.Label:
                i.destroy()

        if delete:
            for i in self.blocks:
                if self.blocks[i]["frame"]==frame:
                    del self.blocks[i]
                    break
            self.frame_data.remove(frame)
            frame.destroy()
            
    def move(self, frame, index):
        new_list = []
        for i in self.frame_data:
            new_list.append(i)
        old_index = new_list.index(frame)
        
        if index=="up":
            new_index = old_index - 1
            if new_index>=0:
                new_list.insert(new_index, new_list.pop(old_index))
        else:
            new_index = old_index + 1
            if new_index<len(new_list):
                new_list.insert(new_index, new_list.pop(old_index))
                
        self.frame_data = new_list
    
        for i in self.frame_data:
            i.pack_forget()
            i.pack(expand=True, fill="both", pady=5)
            
        
    def new_content(self, data, frame=None):

        try:
            if os.path.exists(data):
                img = customtkinter.CTkImage(Image.open(data), size=(100, 100))
            else:
                file = urlopen(data)
                raw_data = file.read()
                file.close()
                img = customtkinter.CTkImage(Image.open(io.BytesIO(raw_data)), size=(100, 100))
        except:
            return

        label = customtkinter.CTkLabel(self.content_frame, width=100, height=100,
                                       image=img, text=None)
        label.pack(side="left", fill="y", padx=5)
        
        label.data = data
        
        clone = customtkinter.CTkLabel(self, width=80, height=80, image=label.cget("image"), text=label.cget("text"))

        if platform.startswith("win"):
            pywinstyles.set_opacity(clone, 0.6)
            
        label.bind("<B1-Motion>", lambda e, clone=clone: self.dnd_handler(clone))
        label.bind("<ButtonRelease-1>", lambda e, clone=clone, tile=label: self.check_area(clone, tile))
        label.bind("<Delete>", lambda e, tile=label, file=data, clone=clone: self.delete(tile, file, clone))
        
        if frame:
            self.check_area(clone, label, frame)
        else:
            self.blocks["ALL"]["content"].append(data)
            
    def do_popup(self, event, frame):
        frame.tk_popup(event.x_root+6, event.y_root+5)
        
    def dnd_handler(self, clone):
        clone.lift()
        x = self.winfo_pointerx() - self.winfo_rootx() -40
        y = self.winfo_pointery() - self.winfo_rooty() -40
        clone.place(x=x, y=y)

        frame = None
        for i in self.frame_data:
            if clone.winfo_y()>i.winfo_y():
                frame = i
            i.configure(border_width=0)
            
        if frame and (clone.winfo_y()<(frame.winfo_y() + frame.winfo_height() + 5)):
            frame.configure(border_width=2)
            
    def check_area(self, clone, tile, frame=None):

        clone.place_forget()
        
        defined_frame = frame

        if defined_frame:
            self.after(100, lambda clone=clone: clone.place(x=-100, y=frame.winfo_y()+10))
            self.after(200, lambda clone=clone: clone.place_forget())
            
        for i in self.frame_data:
            if clone.winfo_y()>i.winfo_y():
                frame = i
            i.configure(border_width=0)
        
        if frame and (clone.winfo_y()>(frame.winfo_y() + frame.winfo_height() + 5)):
            frame = self.content_frame
            
        if frame is None:
            frame = self.content_frame

        if str(tile.winfo_parent())==str(frame):
            return
            
        tile.destroy()
        file = tile.data
      
        if not defined_frame:
            for i in self.blocks:
                if file in self.blocks[i]["content"]:
                    self.blocks[i]["content"].remove(file)
                    
        img = ImageTk.PhotoImage(clone.cget("image")._light_image.resize((clone.cget("width")+20,clone.cget("height")+20)))
        
        if frame==self.content_frame:
            frame_color = customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"][1]
        else:
            frame_color = self.frame_color
            
        tile = tkinter.Label(frame, bg=frame_color, image=img, height=20, width=100, text=None)
        tile.image = img
        
        tile.data = file
        
        tile.pack(fill="y", side="left", padx=5, pady=2)

        tile.bind("<B1-Motion>", lambda e, clone=clone: self.dnd_handler(clone))
        tile.bind("<ButtonRelease-1>", lambda e, clone=clone, tile=tile: self.check_area(clone, tile))
        tile.bind("<Delete>", lambda e, tile=tile, file=file, clone=clone: self.delete(tile, file, clone))
 
        if not defined_frame:
            for i in self.blocks:
                if self.blocks[i]["frame"]==frame:
                    self.blocks[i]["content"].append(file)
        
        del img

    def delete(self, tile, file, clone):
         tile.destroy()
         clone.destroy()
         for i in self.blocks:
            if file in self.blocks[i]["content"]:
                self.blocks[i]["content"].remove(file)
         
if __name__=="__main__":
    root = App()
    root.mainloop()
