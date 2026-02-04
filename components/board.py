import re
import logging
import time

def render(cf, draw, device, y, font, rectangle_y, term=None):
    try:
        if 'piboardinformation' not in globals():
            try:
                with open('/sys/firmware/devicetree/base/model') as fobj:
                    output = ''.join(line.rstrip() for line in fobj)
                output = output.replace('Raspberry Pi ', 'RPi ')
                output = output.replace(' Model ', '')
                output = output.replace(' Plus', '+')
                output = output.replace('Rev ', '')
                output = output.replace('  ', ' ')
                output = re.sub('[^a-zA-Z0-9.+ ]+', '', output)
                globals()['piboardinformation'] = output
            except Exception:
                globals()['piboardinformation'] = 'unknown'
        piboardinformation = globals().get('piboardinformation', 'unknown')
        if cf.get('design') == 'beauty':
            draw.text((0, y), 'Brd', font=font, fill=cf['font']['color'])
            draw.text((cf['boxmarginleft'], y), piboardinformation, font=font, fill=cf['font']['color'])
            y += cf['linefeed']
        elif cf.get('design') == 'terminal' and term is not None:
            term.println('Board: ' + piboardinformation)
            time.sleep(2)
        logging.debug('Board: %s', piboardinformation)
    except Exception:
        logging.exception('Error rendering board')
        draw.text((0, y), 'board err', font=font, fill='RED')
        y += cf.get('linefeed', 8)
    return y
