import subprocess
import re
import logging
import time

def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    try:
        mac = cf.get('component_checkmac', {}).get('mac', '')
        try:
            out = subprocess.check_output(
                f"iw dev wlan0 station get '{mac}' | grep 'signal:' | awk '{{print $2}}'",
                shell=True, stderr=subprocess.DEVNULL
            )
            signal = int(re.sub('[^0-9]+', '', out.decode() or '0'))
        except Exception:
            signal = 0
        try:
            out2 = subprocess.check_output(
                f"iw dev wlan0 station get '{mac}' | grep 'inactive time:' | awk '{{print $3}}'",
                shell=True, stderr=subprocess.DEVNULL
            )
            inactivetime = int(re.sub('[^0-9]+', '', out2.decode() or '99999'))
        except Exception:
            inactivetime = 99999
        string = f"{mac} {signal} {inactivetime}"
        draw.text((0, y), f"{mac} {signal} {round(inactivetime/1000)}", font=font, fill=cf['font']['color'])
        y += cf['linefeed']
        logging.debug('MAC: %s', string)
    except Exception:
        logging.exception('Error rendering checkmac')
        draw.text((0, y), 'checkmac err', font=font, fill='RED')
        y += cf.get('linefeed', 8)
    return y
