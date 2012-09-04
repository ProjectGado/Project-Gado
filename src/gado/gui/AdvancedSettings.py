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
        t = s.get('image_path')
        if not t: t = ''
        e.insert(0, t)
        e.pack()
        self.imagepath_box = e
        self.entries.append(e)
        Button(window, text = "Browse", command = self.imagepath).pack()
        
        # Front Side Image Configuration #
        self.window_f = Toplevel(root)
        window_f = self.window_f
        window_f.title('Advanced Settings - Frontside Images')
        window_f.protocol("WM_DELETE_WINDOW", self.window_f.withdraw)
        
        Label(window_f, text='Frontside Image Settings').pack()
        settings = [('image_front_prefix', 'Prefix'),
                    ('image_front_postfix', 'Postfix'),
                    ('image_front_fn', 'Naming ["set_incrementer" or "id"]'),
                    ('image_front_delim', 'Delim ["/" for directory structure'),
                    ('image_front_filetype', 'Filetype ["jpg" or "tiff"]'),
                    ('image_front_dpi', 'DPI [150, 300, 600]')]
        
        for setting, label in settings:
            Label(window_f, text=label).pack()
            e = Entry(window_f, name=setting)
            t = s.get(setting)
            if not t: t = ''
            e.insert(0, t)
            e.pack()
            self.entries.append(e)
        
        Button(window_f, text='Save', command=self.save).pack()
        Button(window_f, text='Close', command=self.window_f.withdraw).pack()
        window_f.withdraw()
        # \Front Side Image Configuration #
        
        # Backside image configuration
        self.window_b = Toplevel(root)
        window_b = self.window_b
        window_b.title('Advanced Settings - Backside Images')
        window_b.protocol("WM_DELETE_WINDOW", self.window_b.withdraw)
        
        Label(window_b, text='Backside Image Settings').pack()
        settings = [('image_back_prefix', 'Prefix'),
                    ('image_back_postfix', 'Postfix'),
                    ('image_back_fn', 'Naming ["set_incrementer" or "id"]'),
                    ('image_back_delim', 'Delim ["/" for directory structure'),
                    ('image_back_filetype', 'Filetype ["jpg" or "tiff"]'),
                    ('image_back_dpi', 'DPI [150, 300, 600]')]
        
        for setting, label in settings:
            Label(window_b, text=label).pack()
            e = Entry(window_b, name=setting)
            t = s.get(setting)
            if not t: t = ''
            e.insert(0, t)
            e.pack()
            self.entries.append(e)
            
        Button(window_b, text='Save', command=self.save).pack()
        Button(window_b, text='Close', command=self.window_b.withdraw).pack()
        window_b.withdraw()
        # \Backside
        
        # Robot Options
        self.window_o = Toplevel(root)
        window_o = self.window_o
        window_o.title('Advanced Settings - Robot Options')
        window_o.protocol("WM_DELETE_WINDOW", self.window_o.withdraw)
        
        settings = [('arm_home_value', 'arm_home_value'),
                    ('arm_in_value', 'arm_in_value'),
                    ('arm_out_value', 'arm_out_value'),
                    ('actuator_home_value', 'actuator_home_value'),
                    ('actuator_up_value', 'actuator_up_value'),
                    ('baudrate', 'baudrate'),
                    ('gado_port', 'gado_port')]
        
        for setting, label in settings:
            Label(window_o, text=label).pack()
            e = Entry(window_o, name=setting)
            t = s.get(setting)
            if not t: t = ''
            e.insert(0, t)
            e.pack()
            self.entries.append(e)
        
        Button(window_o, text='Save', command=self.save).pack()
        Button(window_o, text='Close', command=self.window_o.withdraw).pack()
        window_o.withdraw()
        # \Backside
        
        
        # Misc Options
        self.window_m = Toplevel(root)
        window_m = self.window_m
        window_m.title('Advanced Settings - Misc Settings')
        window_m.protocol("WM_DELETE_WINDOW", self.window_m.withdraw)
        
        Label(window_m, text='Miscellaneous Settings').pack()
        Label(window_m, text='Saves database to:').pack()
        e = Entry(window_m, name="db_directory")
        e.pack()
        self.dbpath_box = e
        self.entries.append(e)
        Button(window_m, text = "Browse", command = self.dbpath).pack()
        
        settings = [('scanner_name', 'Scanner Name'),
                    ('webcam_name', 'Webcam Name'),]
        
        for setting, label in settings:
            Label(window_m, text=label).pack()
            e = Entry(window_m, name=setting)
            t = s.get(setting)
            if not t: t = ''
            e.insert(0, t)
            e.pack()
            self.entries.append(e)
        
        Button(window_m, text='Save', command=self.save).pack()
        Button(window_m, text='Close', command=self.window_m.withdraw).pack()
        window_m.withdraw()
        # \Misc Options
        
        
        self.window = window
        window.protocol("WM_DELETE_WINDOW", self.window.withdraw)
        
        Button(window, text='Frontside Image Settings', command=self.window_f.deiconify).pack()
        Button(window, text='Backside Image Settings', command=self.window_b.deiconify).pack()
        Button(window, text='Robot Options', command=self.window_o.deiconify).pack()
        Button(window, text='Misc Settings', command=self.window_m.deiconify).pack()
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