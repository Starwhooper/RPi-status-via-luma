from datetime import datetime
import logging

def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    try:
        # Datum/Zeit formatiert
        now = datetime.now()
        string = now.strftime("%a,%d.%b'%y %H:%M:%S")

        # Deutsche Abkürzung korrigieren (Mo, Di, Mi…)
        string = string.replace(string[:3], string[:2])

        # Text zeichnen
        color = cf.get('font', {}).get('color', 'white')
        linefeed = cf.get('linefeed', 8)

        draw.text((0, y), string, font=font, fill=color)
        y += linefeed

        logging.debug("Date: %s", string)

    except Exception:
        logging.exception("Error rendering currentdatetime")
        draw.text((0, y), "datetime err", font=font, fill="RED")
        y += cf.get('linefeed', 8)

    return y
