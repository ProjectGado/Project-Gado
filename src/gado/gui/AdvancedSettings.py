import sys
from Tkinter import *
import tkMessageBox
import ttk
import Pmw
import gado.messages as messages
from gado.functions import *
import tkFileDialog

class AdvancedSettings():
    def __init__(self, root, q_in, q_out, q_gui):
        self.root = root
        self.q_in = q_in
        self.q_out = q_out
        self.q_gui = q_gui
        
        window = Toplevel(root)
        window.title("Advanced Settings")
        
        
        s = import_settings()
        
        self.entries = []
        Label(window, text='Saves images to:').pack()
        e = Entry(window, name="image_path")
        e.pack()
        self.imagepath_box = e
        self.entries.append(e)
        Button(window, text = "Browse", command = self.imagepath).pack()
        
        
        Label(window, text='Frontside Image Settings').pack()
        settings = [('image_front_prefix', 'Prefix'),
                    ('image_front_postfix', 'Postfix'),
                    ('image_front_fn', 'Naming ["set_incrementer" or "id"]'),
                    ('image_front_delim', 'Delim ["/" for directory structure'),
                    ('image_front_filetype', 'Filetype ["jpg" or "tiff"]'),
                    ('image_front_dpi', 'DPI [150, 300, 600]')]
        
        for setting, label in settings:
            Label(window, text=label).pack()
            e = Entry(window, name=setting)
            t = s.get(setting)
            if not t: t = ''
            e.insert(0, t)
            e.pack()
            self.entries.append(e)
        
        Label(window, text='Backside Image Settings').pack()
        settings = [('image_back_prefix', 'Prefix'),
                    ('image_back_postfix', 'Postfix'),
                    ('image_back_fn', 'Naming ["set_incrementer" or "id"]'),
                    ('image_back_delim', 'Delim ["/" for directory structure'),
                    ('image_back_filetype', 'Filetype ["jpg" or "tiff"]'),
                    ('image_back_dpi', 'DPI [150, 300, 600]')]
        
        for setting, label in settings:
            Label(window, text=label).pack()
            e = Entry(window, name=setting)
            t = s.get(setting)
            if not t: t = ''
            e.insert(0, t)
            e.pack()
            self.entries.append(e)
        
        settings = [('arm_home_value', 'arm_home_value'),
                    ('arm_in_value', 'arm_in_value'),
                    ('arm_out_value', 'arm_out_value'),
                    ('actuator_home_value', 'actuator_home_value'),
                    ('actuator_up_value', 'actuator_up_value'),
                    ('baudrate', 'baudrate'),
                    ('gado_port', 'gado_port')]
        
        for setting, label in settings:
            Label(window, text=label).pack()
            e = Entry(window, name=setting)
            t = s.get(setting)
            if not t: t = ''
            e.insert(0, t)
            e.pack()
            self.entries.append(e)
        
        Label(window, text='Miscellaneous Settings').pack()
        Label(window, text='Saves database to:').pack()
        e = Entry(window, name="db_directory")
        e.pack()
        self.dbpath_box = e
        self.entries.append(e)
        Button(window, text = "Browse", command = self.dbpath).pack()
        
        
        settings = [('scanner_name', 'Scanner Name'),
                    ('webcam_name', 'Webcam Name'),]
        
        for setting, label in settings:
            Label(window, text=label).pack()
            e = Entry(window, name=setting)
            t = s.get(setting)
            if not t: t = ''
            e.insert(0, t)
            e.pack()
            self.entries.append(e)
        
        self.window = window
        window.protocol("WM_DELETE_WINDOW", self.window.withdraw)
        
        Button(window, text='Save', command=self.save).pack()
        Button(window, text='Close', command=self.window.withdraw).pack()
        
        window.withdraw()
    
    def show(self):
        self.window.deiconify()
    
    def save(self):
        s = dict()
        for e in self.entries:
            s[e._name] = e.get()
        export_settings(**s)
        
    def imagepath(self):
        dirname = tkFileDialog.askdirectory(parent=self.window,
                                            initialdir=".",
                                            title='Please select a directory')
        self.imagepath_box.delete(0, 'end')
        self.imagepath_box.insert('end', dirname)
    
    def dbpath(self):
        dirname = tkFileDialog.askdirectory(parent=self.window,
                                            initialdir=".",
                                            title='Please select a directory')
        self.dbpath_box.delete(0, 'end')
        self.dbpath_box.insert('end', dirname)