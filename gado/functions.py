import json

def import_settings():
    # image_path
    FH = open('gado.conf')
    conf = FH.read()
    FH.close()
    settings = json.loads(conf)
    return settings