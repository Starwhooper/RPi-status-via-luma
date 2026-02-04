import logging
import time

def render(cf, draw, device, y, font, rectangle_y, term=None):
    try:
        if cf.get('design') == 'beauty':
            draw.text((0, y), 'Hello World', font=font, fill='Yellow')
            y += cf['linefeed']
        elif cf.get('design') == 'terminal' and term is not None:
            term.println('Hello World')
            time.sleep(2)
        logging.debug('Hello World')
    except Exception:
        logging.exception('Error rendering helloworld')
        draw.text((0, y), 'hello err', font=font, fill='RED')
        y += cf.get('linefeed', 8)
    return y
