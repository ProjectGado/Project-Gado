'''
Created on Sep 11, 2010

@author: Tom Smith
'''

#!/usr/bin/python
import zbar
import Image

def findBarcodes(filename):
    # create a reader
    scanner = zbar.ImageScanner()
    
    # configure the reader
    scanner.parse_config('enable')
    
    # obtain image data
    pil = Image.open(filename).convert('L')
    width, height = pil.size
    raw = pil.tostring()
    
    # wrap image data
    image = zbar.Image(width, height, 'Y800', raw)
    
    # scan the image for barcodes
    scanner.scan(image)
    
    # extract results
    result = []
    for symbol in image:
        # do something useful with results
        print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
        result.append(symbol.data)
    
    # clean up
    del(image)
    
    return result

        