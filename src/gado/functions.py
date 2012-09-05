import json, os, datetime, time, sys
from subprocess import Popen, PIPE
from gado.db import DBInterface

def fetch_from_queue(q, message=None, timeout=None):
    '''
    Fetches a message from the passed queue
    
    If the message argument is supplied, this function will
    wait until it finds that message.
    '''
    while True:
        msg = q.get()
        if (message == None) or (msg[0] == message):
            return msg
        else:
            q.put(msg)

def add_to_queue(q, message, arguments=None):
    '''
    Adds a message to the queue with any passed arguments
    '''
    q.put((message, arguments))

def gadodir():
    '''
    The directory that the gado stuff should be stored in.
    
    This only works for Windows right now - it uses APPDATA
    '''
    n = os.name
    if n == 'nt':
        return os.path.join(os.environ['APPDATA'], 'Gado')
    else:
        return '.'

def _settingspath():
    d = gadodir()
    p = os.path.join(d, 'gado.conf')
    try:
        os.makedirs(d)
    except:
        pass
    return p

def import_settings():
    '''
    Reads and returns the settings from the conf file
    
    If the conf file does not exist, then this returns an empty dict
    '''
    try:
        # image_path
        FH = open(_settingspath())
        conf = FH.read()
        FH.close()
        settings = json.loads(conf)
        return settings
    except:
        return dict()
        

#Pass in a dictionary containing the values being changed
#Can add in new key value pairs also
def export_settings(**kwargs):
    '''
    Exports any passed settings.
    
    This function merges the passed settings with current
    settings and then saves them to the conf file.
    '''
    
    #Import the current configuration dictionary
    conf = import_settings()
    
    #Merge the two dictionaries (Kwargs gets priority)
    newConf = dict(conf.items() + kwargs.items())
    
    #Open settings file for writing
    FH = open(_settingspath(), 'w')
    
    #Dump the merged settings dictionary into the settings file
    FH.write(json.dumps(newConf))
    
    #Close up file connection
    FH.close()

def new_artifact(dbi, artifact_set):
    '''
    Creates a new artifact and returns a dictionary
    
    dictionary elements:
        artifact_id, front_id, back_id, front_path,
        back_path
    '''
    i, inc = dbi.add_artifact(artifact_set)
    settings = import_settings()
    image_path = settings.get('image_path')
    if not image_path: settings['image_path'] = imagespath()
    
    front_path, back_path = _image_paths(dbi, i, artifact_set, inc, **settings)
    front_id = dbi.add_image(i, front_path, front=True)
    back_id = dbi.add_image(i, back_path, front=False)
    dbi.commit()
    return dict(artifact_id = i, front_id = front_id, back_id = back_id,
                front_path = front_path, back_path = back_path)
    
def _image_paths(dbi, artifact_id, artifact_set, incrementer, image_path='',
                 image_front_prefix='', image_front_postfix='_front',
                 image_back_prefix='', image_back_postfix='_back',
                 image_front_delim='', image_back_delim='',
                 image_front_filetype='tiff', image_back_filetype='jpg',
                 image_front_fn='set_incrementer',
                 image_back_fn='set_incrementer',
                 **kwargs):
    '''
    Returns the full paths for front and back as a tuple
    
    The available settings are [DEFAULTS]
        image_front_prefix ['']
        image_front_postfix ['_front']
        image_back_prefix ['']
        image_back_postfix ['_back']
        image_front_delim ['']
        image_back_delim ['']
        image_front_concat = [1] # other option is 0 for false
        image_back_concat = [1] # other option is 0 for false
        image_front_filetype ['.tiff']
        image_back_filetype ['.jpg']
        image_front_fn = ['set_incrementer'] # other option is id
        image_back_fn = ['set_incrementer'] # other option is id
        image_path = ['images']
    '''
    image_path.replace('\\', '/')
    if image_path[-1] == '/': image_path = image_path[:-1]
    image_front_delim.replace('\\', '/')
    image_back_delim.replace('\\', '/')
    
    image_front_filetype.replace('.', '')
    image_back_filetype.replace('.', '')
    
    parents = dbi.artifact_parents(artifact_id)
    # p[0] is the id, p[1] is the name of the set
    p_names = [p[1] for p in parents]
    
    if image_front_fn == 'set_incrementer':
        fn = '%s' % incrementer
    else:
        fn = '%s' % artifact_id
    
    if image_front_delim == '/':
        path = '%s/%s/' % (image_path, image_front_delim.join(p_names))
        try: os.makedirs(path)
        except: print 'functions\tpath already exists: "%s"' % path
        front_path = '%s%s%s%s.%s' % (path, image_front_prefix, fn,
                                      image_front_postfix,
                                      image_front_filetype)
    else:
        path = '%s/' % (image_path)
        try: os.makedirs(path)
        except: print 'functions\tpath already exists: "%s"' % path
        join = image_front_delim.join(p_names)
        front_path = '%s%s%s%s%s.%s' % (path, image_front_prefix, join,
                                        fn, image_front_postfix,
                                        image_front_filetype)
    
    if image_back_fn == 'set_incrementer':
        fn = '%s' % incrementer
    else:
        fn = '%s' % artifact_id
    
    if image_back_delim == '/':
        path = '%s/%s/' % (image_path, image_back_delim.join(p_names))
        try: os.makedirs(path)
        except: print 'functions\tpath already exists: "%s"' % path
        back_path = '%s%s%s%s.%s' % (path, image_back_prefix, fn,
                                      image_back_postfix,
                                      image_back_filetype)
    else:
        path = '%s/' % (image_path)
        try: os.makedirs(path)
        except: print 'functions\tpath already exists: "%s"' % path
        join = image_back_delim.join(p_names)
        back_path = '%s%s%s%s%s.%s' % (path, image_back_prefix, join,
                                        fn, image_back_postfix,
                                        image_back_filetype)
    
    
    return (front_path, back_path)


def check_for_barcode(image_path, code='project gado'):
    args = ['lib\zbar\zbarimg.exe', '-q', image_path]
    cmd = ' '.join(args)
    print "CMD: %s" % (cmd)
    #Test code to make this runnable with py2exe
    if hasattr(sys.stderr, 'fileno'):
        procStdErr = sys.stderr
    elif hasattr(sys.stderr, '_file') and hasattr(sys.stderr._file, 'fileno'):
        proceStdErr = sys.stderr._file
    else:
        procStdErrPath = 'nul'
        procStdErr = file(procStdErrPath, 'a')
    
    proc = Popen(cmd, stdout=PIPE, stderr=procStdErr, shell=True)
    output, errors = proc.communicate()
    output = str(output)
    print 'functions\tcheck_for_barcode received: %s' % output
    print "barcode was %sfound" % ('' if output.find(code) >= 0 else 'not ')
    return (len(output) > 0) and (output.find(code) >= 0)