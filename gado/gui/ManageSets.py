import sys
from Tkinter import *
import tkMessageBox
import ttk
import Pmw
import gado.messages as messages
from gado.functions import *

class ManageSets():
    def __init__(self, root, q_in, q_out):
        self.q_in = q_in
        self.q_out = q_out
        
        window = Toplevel(root)
        window.title("Manage Artifact Sets")
        self.window = window
        
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
    
    def show(self):
        self.window.deiconify()
        self._refresh()
    
    def _set_selected(self):
        idx = self.sets_box.curselection()[0]
        self.selected_set = self.artifact_sets[int(idx)][0]
        
    def _refresh(self):
        # Clear current list
        self.sets_box.delete(0, 'end')
        
        # Get the list of sets and add to the box
        add_to_queue(self.q_out, messages.ARTIFACT_SET_LIST)
        msg = fetch_from_queue(self.q_in, messages.RETURN, timeout=10)
        self.artifact_sets = msg[1]
        for id, indented_name in self.artifact_sets:
            self.sets_box.insert('end', indented_name)
    
    def _create_new_set(self):
        '''Adds a new Artifact Set to the db and refreshes the view'''
        name = self.name_textbox.get()
        if not name:
            print 'how do we show an error? the set must be named'
            return
        add_to_queue(self.q_out,  messages.RETURN, dict(name=name,parent=self.selected_set))
        msg = fetch_from_queue(self.q_in, messages.RETURN, timeout=10)
        self._refresh()
    
    def _delete_set(self):
        add_to_queue(self.q_out, messages.DELETE_ARTIFACT_SET_LIST, self.selected_set)
        self._refresh()