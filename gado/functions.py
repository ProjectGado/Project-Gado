import json, os

from subprocess import Popen, PIPE

def import_settings():
    try:
        # image_path
        FH = open('gado.conf')
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
    
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    output, errors = proc.communicate()
    output = str(output)
    print "barcode was %sfound" % ('' if output.find(code) >= 0 else 'not ')
    return output.find(code) >= 0