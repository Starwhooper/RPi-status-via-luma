from datetime import datetime
import time
import logging

def render(cf, draw, device, y, font, rectangle_y, term=None):
    try:
        string = '{:%a,%d.%b\'%y %H:%M:%S}'.format(datetime.now())
        string = string.replace(string[:3], string[:2])
        if cf.get('design') == 'beauty':
            draw.text((0, y), string, font=font, fill=cf['font']['color'])
            y += cf['linefeed']
        elif cf.get('design') == 'terminal' and term is not None:
            term.println('Date: ' + string)
            time.sleep(2)
        logging.debug('Date: %s', string)
    except Exception:
        logging.exception('Error rendering currentdatetime')
        draw.text((0, y), 'datetime err', font=font, fill='RED')
        y += cf.get('linefeed', 8)
    return y
