import json, os, datetime, time, sys

from subprocess import Popen, PIPE


def fetch_from_queue(q, message=None, timeout=None):
    start = datetime.datetime.now()
    while True:
        # we check for emptiness, instead of continuous .get()
        # so that we can timeout if needed
        
        '''
        if not q.empty():
            msg = q.get()
            print 'somebody is fetching from queue: %s' % msg
            if (message and msg[0] == message) or (not message):
                return msg
            else:
                q.put(msg)
        if timeout and datetime.datetime.now() - start > timeout:
            #l.release()
            raise Exception("message never received")
        '''
        msg = q.get()
        #print 'functions\tsomebody is fetching from queue:', msg
        if (message and msg[0] == message) or (not message):
            return msg
        else:
            q.put(msg)

def add_to_queue(q, message, arguments=None):
    #print 'functions\tsomebody is adding %s to queue with arguments: %s' % (message, str(arguments))
    time.sleep(1)
    q.put((message, arguments))
    pass

def _gadodir():
    n = os.name
    if n == 'nt':
        return os.path.join(os.environ['APPDATA'], 'Gado')
    else:
        return '.'

def _settingspath():
    d = os.path.join(_gadodir(), 'gado.conf')
    os.makedirs(d)
    return d

def _imagespath():
    d = os.path.join()

def import_settings():
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
    
    #Import the current configuration dictionary
    conf = import_settings()
    
    #Merge the two dictionaries (Kwargs gets priority)
    newConf = dict(conf.items() + kwargs.items())
    
    #Open settings file for writing
    FH = open('gado.conf', 'w')
    
    #Dump the merged settings dictionary into the settings file
    FH.write(json.dumps(newConf))
    
    #Close up file connection
    FH.close()

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
    print "barcode was %sfound" % ('' if output.find(code) >= 0 else 'not ')
    return output.find(code) >= 0