import re
import logging

# Cache für Board-Information
_BOARD_INFO_CACHE = None

def _get_board_information():
    global _BOARD_INFO_CACHE
    
    if _BOARD_INFO_CACHE is not None:
        return _BOARD_INFO_CACHE
    
    try:
        with open('/sys/firmware/devicetree/base/model') as fobj:
            output = ''.join(line.rstrip() for line in fobj)
        
        # Normalisierungen anwenden
        replacements = [
            ('Raspberry Pi ', 'RPi '),
            (' Model ', ''),
            (' Plus', '+'),
            ('Rev ', ''),
            ('  ', ' ')
        ]
        
        for old, new in replacements:
            output = output.replace(old, new)
        
        # Nur alphanumerische Zeichen, Punkte und Leerzeichen behalten
        output = re.sub(r'[^a-zA-Z0-9.+ ]+', '', output)
        _BOARD_INFO_CACHE = output
        
    except Exception as e:
        logging.warning('Could not read board information: %s', str(e))
        _BOARD_INFO_CACHE = 'unknown'
    
    return _BOARD_INFO_CACHE

def render(cf, draw, device, y, font, rectangle_y=None, term=None):

    try:
        piboardinformation = _get_board_information()
        
        draw.text((0, y), 'Brd', font=font, fill=cf['font']['color'])
        draw.text((cf['boxmarginleft'], y), piboardinformation, font=font, fill=cf['font']['color'])
        y += cf['linefeed']
        
        logging.debug('Board: %s', piboardinformation)
        
    except Exception as e:
        logging.exception('Error rendering board: %s', str(e))
        draw.text((0, y), 'board err', font=font, fill='RED')
        y += cf.get('linefeed', 8)
    
    return y
