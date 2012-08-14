import json, random

def import_settings():
    # image_path
    FH = open('gado.conf')
    conf = FH.read()
    FH.close()
    settings = json.loads(conf)
    return settings

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

def check_for_barcode(image_path):
    '''
    Checks the image for a barcode.
    
    Returns True if a barcode is found, otherwise False
    '''
    
    # TODO
    
    return random.random() > 0.9