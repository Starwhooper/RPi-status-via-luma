import platform
import logging
import time

def render(cf, draw, device, y, font, rectangle_y, term=None):
    try:
        kervelversion = platform.release()
        if cf.get('design') == 'beauty':
            draw.text((0, y), 'krnl', font=font, fill=cf['font']['color'])
            draw.text((cf['boxmarginleft'], y), kervelversion, font=font, fill=cf['font']['color'])
            y += cf['linefeed']
        elif cf.get('design') == 'terminal' and term is not None:
            term.println('Kernel: ' + kervelversion)
            time.sleep(2)
        logging.debug('Kernel: %s', kervelversion)
    except Exception:
        logging.exception('Error rendering kernelversion')
        draw.text((0, y), 'krnl err', font=font, fill='RED')
        y += cf.get('linefeed', 8)
    return y
