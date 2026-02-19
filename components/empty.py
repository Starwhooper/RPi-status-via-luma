import logging

def render(cf, draw, device, y, font, rectangle_y, term=None):
    try:
        # Leere Zeile (nur Abstand)
        y += cf['linefeed']
        logging.debug('Empty line')
    except Exception:
        logging.exception('Error rendering empty line')
        y += cf.get('linefeed', 8)
    return y
