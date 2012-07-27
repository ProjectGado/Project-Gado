import sqlite3, json
import os.path
from gado.db import DBFactory
from gado.functions import *

'''
THIS FILE IS FOR TESTING FUNCTIONS ONLY.
IT IS NOT PRODUCTION CODE.

CHECK OUT gado/functions.py FOR REAL CODE
'''

def add_records():
    # add a couple entries to the db to see if the db works
    db.artifact_sets.insert(name='first set')
    db.artifact_sets.insert(name='second set')
    db.artifact_sets.insert(name='third set')
    db.commit()
    
def print_records():
    # print the records in artifact_sets
    sets = db(db.artifact_sets.id > 0).select()
    for s in sets:
        print '%s - %s' % (s['id'], s['name'])

if __name__ == '__main__':
    '''
    So this is kind of neat. import_settings creates a dictionary from the
    gado configuration file. All of those settings can be passed to the
    DBFactory - if you look at the code for DBFactory you'll notice that it
    has **kwargs in its argument list. This allows it to accept all of the
    settings and then only use the ones that are relevant (if any are)
    '''
    settings = import_settings()
    print settings
    db = DBFactory(**settings).get_db()
    
    # This puts the db in globals. Makes it easier to access
    globals()['db'] = db
    
    # Some random functions to see if the db works.
    add_records()
    print_records()