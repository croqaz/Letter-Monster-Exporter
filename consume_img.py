#/usr/bin/env python

"""
    [ Letter Monster V2 ]
    Copyright (C) 2013, Cristi Constantin.
    All Rights Reserved.
"""

import time
import struct
import binascii
from PIL import Image, ImageFilter
import numpy as np


# All valid PIL filters
Filters = ('BLUR', 'SHARPEN', 'EDGE_ENHANCE', 'SMOOTH', 'SMOOTH_MORE', 'DETAIL', 'CONTOUR', 'EDGE_ENHANCE_MORE')

Patterns = {
    'default'    : u'&80$21|;:\' ',     # Original Patrick T. Cossette pattern
    'saufanlee'  : u'#WKDGLftji+;,:. ', # Sau Fan Lee pattern
    'dark'       : u'WWWwww ',          # Good for color HTML
    'huge'       : u'MMMMMMM@@@@@@@WWWWWWWWWBBBBBBBB000000008888888ZZZZZZZZZaZaaaaaa2222222SSSSSSSXXXXXXXXXXX7777777rrrrrrr;;;;;;;;iiiiiiiii:::::::,:,,,,,,.........    ',
    'dos'        : u'\u2588\u2593\u2592\u2665\u2666\u263b\u256c\u263a\u25ca\u25cb\u2591 '
}



def Consume(image, output, x=0, y=0, pattern='default', filter=''):

    '''
    Takes a supported image as input, transforms it into a Rectangular Unicode Array and exports the result.\n\
    You can use different patterns for transforming : default, dark, huge, etc.\n\
    You can also apply filters : BLUR, SHARPEN, EDGE_ENHANCE, SMOOTH, etc.\n\
    '''

    try:
        vInput = Image.open( image )
    except:
        print( 'Letter-Monster snarls: "`%s` is not a valid image path, or Python-Imaging '
            'cannot open that type of file! Cannot consume!"' % image ) ; return

    ti = time.clock() # Global counter.

    if x and not y:     # If x has a value.
        if DEBUG: print( 'Letter-Monster says: "I\'m resizing to X = %i."' % x )
        y = (x * vInput.size[1]) / vInput.size[0]
        if DEBUG: print( 'Letter-Monster says: "Y becomes %i."' % y )
    elif y and not x:   # Or if y has a value.
        if DEBUG: print( 'Letter-Monster says: "I\'m resizing to Y = %i."' % y )
        x = (y * vInput.size[0]) / vInput.size[1]
        if DEBUG: print( 'Letter-Monster says: "X becomes %i."' % x )

    elif x and y:       # If both x and y have a value.
        if DEBUG: print( 'Letter-Monster says: "Disproportionate resize X = %i, Y = %i."' % (x,y) )
    if x or y:          # If resize was called.
        vInput = vInput.resize((x, y), Image.BICUBIC) # Do the resize.
    del x ; del y

    if filter: # If filter was called.
        for filt in filter.split('|'):
            filt = filt.upper()
            if filt in Filters:
                vInput = vInput.filter( getattr(ImageFilter, filt) )
                if DEBUG: print( 'Letter-Monster says: "Applied %s filter."' % filt )
            else:
                print( 'Letter-Monster growls: "I don\'t know any filter called `%s`! I will ignore it."' % filt )

    if pattern.lower() in Patterns:
        vPattern = Patterns[pattern.lower()]
    else:
        print( 'Letter-Monster growls: "I don\' know any pattern called `%s`! I will use default pattern."' % pattern )
        vPattern = Patterns['default']


    vLen = len( vPattern )
    vLetters = np.empty( (vInput.size[1], vInput.size[0]), 'U' )
    vColors = []

    if vInput.mode=='L' or 'P': # Convert grayscale / indexed images to RGB.
        pxaccess = vInput.convert('RGB').load()
        ch = 3
    else:
        pxaccess = vInput.load()
        ch = len(vInput.getbands())

    fix_clr = lambda x: (x / 51) * 51


    for py in range(vInput.size[1]): # Cycle through the image's pixels, one by one
        for px in range(vInput.size[0]):

            pix_color = pxaccess[px, py] # Pointer to current pixel
            vColor = sum(pix_color)      # Calculate general darkness of the pixel

            fixed_color = [ fix_clr(pix_color[0]), fix_clr(pix_color[1]), fix_clr(pix_color[2]) ]
            vColors.append( binascii.hexlify(struct.pack('BBB', *fixed_color))[::2] )

            for vp in range( vLen ):                       # For each element in the string pattern
                if vColor <= ( 255 * ch / vLen * (vp+1) ): # Return matching character from pattern
                    vLetters[py,px] = vPattern[vp]
                    break
                # If not in range, return last character from pattern
                elif vColor > ( 255 * ch / vLen * vLen ) and vColor <= ( 255 * ch ):
                    vLetters[py,px] = vPattern[-1]
                    break


    # Equalize "non conventional" colors...
    eq_colors = sorted(set(vColors))
    print 'Found `{}` unique colors.'.format(len(eq_colors))

    tf = time.clock()
    if DEBUG: print( 'Letter-Monster says: "Consume took %.4f seconds total."' % (tf-ti) )


    if output.endswith('htm') or output.endswith('html'):

        vOut = open(output, 'w')
        vOut.write('<style>\n')
        for c in eq_colors:
            vOut.write('.c%s {color: #%s; text-shadow: 0 0 3px #%s}\n' % (c, c, c))
        vOut.write('</style>\n<pre>\n')

        last_color = 0
        color_index = 0

        for py in range(vInput.size[1]):
            for px in range(vInput.size[0]):
                curr_color = vColors[color_index]
                if curr_color != last_color:
                    last_color = curr_color
                    if color_index: vOut.write('</b>')
                    vOut.write('<b class="c{}">{}'.format(curr_color, vLetters[py,px]))
                else:
                    vOut.write(vLetters[py,px])
                color_index += 1
            vOut.write('\n')

        vOut.write('</b>\n</pre>')
        vOut.close()

    else:

        vOut = open(output, 'w')
        vOut.close()



if __name__ == '__main__':

    DEBUG = True

    Consume('house1.png', 'export.htm', x=120, y=0, pattern='dark')

