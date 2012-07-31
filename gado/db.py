from lib.dal import DAL, Field
import os

class DBFactory():
    '''
    The factory creates a DAL object for interacting with the database
    
    In the future, different gado users may have different db needs
    '''
    
    def __init__(self, db_directory='databases', db_filename='db.sqlite', **kwargs):
        '''
        The abstraction layer needs to store files somewhere (in db_directory)
        And it also needs a filename for the sqlite file.
        
        These arguments are partially unecessary.
        
        The **kwargs 
        '''
        self.db_directory = db_directory
        self.db_filename = db_filename
        
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)
    
    def get_db(self):
        db = DAL('sqlite://%s' % self.db_filename,
                 folder = self.db_directory)
        
        # An artifact set is a specific set of artifacts
        # ex: a folder of images to be scanned
        db.define_table('artifact_sets',
            Field('name', 'string'),
            Field('parent', 'reference artifact_sets'))
        
        # An artifact is an individual image in the Gado's queue
        # artifact name is a concatenation of set.name and set_incrementor
        # the set_incrementer is an incrementer for a particular set
        # the first object in the queue has an incrementer of 1
        # the last object has a set_incrementer of N (for N objects in the stack)
        db.define_table('artifacts',
            Field('artifact_set', db.artifact_sets), # foreign key
            Field('set_incrementer', 'integer'),
            Field('name', 'string'))
        
        # An image is a picture
        # this could be a scan of the front or a snapshot of the back
        db.define_table('images',
            Field('artifact', db.artifacts),
            Field('artifact_incrementer', 'integer'),
            Field('path', 'string'),
            Field('front', 'boolean'), # is this a picture of the front?
            Field('name', 'string'))
        
        return db

class DBInterface():
    def __init__(self, db):
        self.db = db
        self.delim = '  '
    
    def add_artifact_set(self, name, parent):
        pass
    
    def delete_artifact_set(self, name):
        pass
    
    def _get_children(self, parent):
        db = self.db
        children_rows = db(db.artifact_sets.parent == parent).select()
        children_final = []
        for child in children_rows:
            print "iterating on %s with parent %s!" % (child['name'], child['parent'])
            child_dict = dict(name = child['name'],
                              id = child['id'],
                              children = self._get_children(child['id']))
            children_final.append(child_dict)
        return children_final
    
    def artifact_set_list(self):
        set_list = self._get_children(None)
        final_set_list = self._build_tuple_list(set_list)
        final_set_list.insert(0,(None,'No parent'))
        return final_set_list
    
    def _build_tuple_list(self, set_list, depth=0):
        current_list = []
        for artifact_set in set_list:
            indent = self.delim * depth
            indented_name = '%s%s' % (indent, artifact_set['name'])
            line_item = (artifact_set['id'], indented_name)
            current_list.append(line_item)
            children_list = self._build_tuple_list(artifact_set['children'], depth+1)
            current_list.extend(children_list)
        return current_list
    
    def add_artifact_set(self, name, parent):
        self.db.artifact_sets.insert(name=name, parent=parent)
        self.db.commit()