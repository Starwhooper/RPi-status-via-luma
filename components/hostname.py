import socket
import logging
import time
from PIL import ImageFont

def render(cf, draw, device, y, font, rectangle_y, term=None):
    try:
        hostname = str(socket.gethostname()).upper()
        if cf.get('design') == 'beauty':
            try:
                ch = cf.get('component_hostname', {})
                hf = ch.get('font', {})
                if hf.get('default', False):
                    hostname_font = ImageFont.load_default()
                else:
                    hostname_font = ImageFont.truetype(hf.get('ttffile'), hf.get('size'))
            except Exception:
                logging.exception('Hostname font error')
                hostname_font = ImageFont.load_default()
            text_x = (device.width - draw.textbbox(xy=(0,0), text=hostname, font=hostname_font)[2]) / 2
            text_y = draw.textbbox(xy=(0,0), text=hostname, font=hostname_font)[3]
            draw.text((text_x, y), hostname, font=hostname_font, fill='Yellow')
            y += text_y
        elif cf.get('design') == 'terminal' and term is not None:
            term.println('Hostname: ' + hostname)
            time.sleep(2)
        logging.debug('Hostname: %s', hostname)
    except Exception:
        logging.exception('Error rendering hostname')
        draw.text((0, y), 'hostname err', font=font, fill='RED')
        y += cf.get('linefeed', 8)
    return y
