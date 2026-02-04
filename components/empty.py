import logging
import time

def render(cf, draw, device, y, font, rectangle_y, term=None):
    try:
        if cf.get('design') == 'beauty':
            draw.text((0, y), '', font=font, fill='Yellow')
            y += cf['linefeed']
        elif cf.get('design') == 'terminal' and term is not None:
            term.println('')
            time.sleep(2)
        logging.debug('Empty line')
    except Exception:
        logging.exception('Error rendering empty')
        y += cf.get('linefeed', 8)
    return y
