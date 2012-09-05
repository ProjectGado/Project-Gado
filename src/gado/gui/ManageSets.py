import sys
from Tkinter import *
import tkMessageBox
import ttk
import Pmw
import gado.messages as messages
from gado.functions import *
from threading import Thread
import datetime

class _RefreshHelper(Thread):
    def __init__(self, manager, q_out, q_in, q_gui, new_set=None, delete_set=None):
        self.manager = manager
        self.q_out = q_out
        self.q_in = q_in
        self.q_gui = q_gui
        self.new_set = new_set
        self.delete_set = delete_set
        Thread.__init__(self)
    
    def run(self):
        print 'ManageSets\tStart time: %s' % (datetime.datetime.now())
        if self.new_set:
            add_to_queue(self.q_out, messages.ADD_ARTIFACT_SET_LIST, self.new_set)
        elif self.delete_set:
            add_to_queue(self.q_out, messages.DELETE_ARTIFACT_SET_LIST, self.delete_set)
        
        add_to_queue(self.q_out, messages.ARTIFACT_SET_LIST)
        msg = fetch_from_queue(self.q_in, messages.ARTIFACT_SET_LIST, timeout=10)
        self.manager.add_artifact_sets(msg[1])
    
    def refresh(self):
        
        pass

class ManageSets():
    def __init__(self, root, q_in, q_out, q_gui):
        self.q_in = q_in
        self.q_out = q_out
        self.q_gui = q_gui
        
        window = Toplevel(root)
        window.title("Manage Artifact Sets")
        self.window = window
        
        #Bind key listener to window
        self.window.bind("<Key>", self._keyboard_callback)
        
        self.sets_box = Pmw.ScrolledListBox(
            window,
            items=(),
            labelpos='nw',
            label_text='Select a Parent: ',
            listbox_height=6,
            selectioncommand=self._set_selected,
            usehullsize=1,
            hull_width = 200,
            hull_height = 200)
        
        self.sets_box.grid(row=0, column=0,
                           columnspan=2,
                           sticky=N+S+E+W,
                           padx=10, pady=5)
                
        #Create a label for the name entry
        name_label = Label(window)
        name_label["text"] = "Artifact Set Name: "
        name_label.grid(row=1, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        #Create the entry box for the name input
        name_textbox = Entry(window)
        name_textbox.grid(row=1, column=1, sticky=N+S+E+W, padx=10, pady=5)
        self.name_textbox = name_textbox
        
        #Create the add button
        add_button = Button(window)
        add_button["text"] = "Add"
        add_button["command"] = self._create_new_set
        add_button.grid(row=2, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        #Create the delete button
        delete_btn = Button(window)
        delete_btn["text"] = "Delete"
        delete_btn["command"] = self._delete_set
        delete_btn.grid(row=2, column=1, sticky=N+S+E+W, padx=10, pady=5)
        
        window.protocol("WM_DELETE_WINDOW", self.window.withdraw)
        window.withdraw()
    
    def _keyboard_callback(self, event):
        key = event.keycode
        
        if key == 13: #Key stroke is the enter key
            self._create_new_set()
    
    def add_artifact_sets(self, sets):
        self.artifact_sets = sets
        
        # Clear current list
        self.sets_box.delete(0, 'end')
        for id, indented_name in self.artifact_sets:
            self.sets_box.insert('end', indented_name)
        
        add_to_queue(self.q_gui, messages.REFRESH)
    
    def hide(self):
        add_to_queue(self.q_gui, messages.RELAUNCH_LISTENER)    
        self.window.withdraw()
    
    def show(self):
        self.window.deiconify()
        self._refresh()
    
    def _set_selected(self):
        idx = self.sets_box.curselection()[0]
        self.selected_set = self.artifact_sets[int(idx)][0]
        
    def _refresh(self, new_set=None, delete_set=None):
        self.sets_box.delete(0, 'end')
        self.sets_box.insert('end', 'LOADING, PLEASE WAIT')
        t = _RefreshHelper(self, self.q_out, self.q_in, self.q_gui, new_set, delete_set)
        t.start()
    
    def _create_new_set(self):
        '''Adds a new Artifact Set to the db and refreshes the view'''
        name = self.name_textbox.get()
        if not name:
            add_to_queue(self.q_gui, messages.DISPLAY_ERROR, 'Please name your new artifact set.')
            print 'how do we show an error? the set must be named'
            return
        self._refresh(new_set=dict(name=name, parent=self.selected_set))
    
    def _delete_set(self):
        self._refresh(delete_set=self.selected_set)
        add_to_queue(self.q_gui, messages.REFRESH)