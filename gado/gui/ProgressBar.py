from Tkinter import *
import ttk
import tkMessageBox

class ProgressBar(Frame):
    def __init__(self, root = None, *args, **kwargs):
        #tk.Tk.__init__(self, *args, **kwargs)
        #self.button = ttk.Button(text="start", command=self.start)
        #self.button.pack()
        #self.root = root
        Frame.__init__(self, *args, **kwargs)
        
        #Create the label
        self.label = Label(self)
        self.label["text"] = "Detecting and connecting to Gado..."
        self.label.pack()
        
        #Build the progressbar
        self.progress = ttk.Progressbar(self, orient="horizontal", 
                                        length=200, mode="indeterminate")
        self.progress.pack()
        
        self.pack()
        self.bytes = 0
        self.maxbytes = 0
        self.progress.start()

    def start(self):
        self.progress["value"] = 0
        self.maxbytes = 50000
        self.progress["maximum"] = 50000
        self.read_bytes()

    def read_bytes(self):
        '''simulate reading 500 bytes; update progress bar'''
        self.bytes += 500
        self.progress["value"] = self.bytes
        if self.bytes < self.maxbytes:
            # read more bytes after 100 ms
            self.after(100, self.read_bytes)
    
    def stop(self, success):
        self.quit()
        self.destroy()