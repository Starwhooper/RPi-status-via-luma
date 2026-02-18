import socket
import logging
import time
import os
from PIL import ImageFont

def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    try:
        hostname = socket.gethostname().upper()
        #hostname_font = None

        # Font-Konfiguration lesen
        font_cfg = cf.get('component_hostname', {}).get('font', {})
        ttffile = font_cfg.get('ttffile')
        ttfsize = font_cfg.get('size')
        use_default = font_cfg.get('default', True)

        # TTF laden, falls gewünscht
        if not use_default and ttffile and os.path.exists(ttffile):
            try:
                hostname_font = ImageFont.truetype(ttffile, ttfsize)
            except Exception:
                logging.exception(f"Error loading font '{ttffile}' size {ttfsize}")

        # Fallback
        if not hostname_font:
            hostname_font = ImageFont.load_default()

        # Textmaße bestimmen
        bbox = draw.textbbox((0, 0), hostname, font=hostname_font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Zentrieren
        text_x = (device.width - text_w) // 2

        # Zeichnen
        draw.text((text_x, y -2), hostname, font=hostname_font, fill='Yellow')
        y += text_h

        logging.debug('Hostname: %s', hostname)

    except Exception:
        logging.exception('Error rendering hostname')
        draw.text((0, y), 'hostname err', font=font, fill='RED')
        y += cf.get('linefeed', 8)

    return y
