from datetime import datetime
import time
import psutil
import logging

def render(cf, draw, device, y, font, rectangle_y, term=None):
    """
    Render the uptime component.
    - cf: configuration dict
    - draw: PIL drawing context
    - device: luma device
    - y: current y position (int)
    - font: PIL font
    - rectangle_y: height of a line (int)
    - term: optional terminal virtual device (for 'terminal' design)
    Returns: new y position (int)
    """
    def format_time_ago(seconds):
        if seconds < 60:
            return f'{int(seconds)} seconds'
        elif seconds < 3600:
            return f'{int(seconds/60)} minutes'
        elif seconds < 86400:  # 3600 * 24
            return f'{seconds / 3600:.1f} hours'
        elif seconds < 604800:  # 3600 * 24 * 7
            return f'{seconds / 86400:.1f} days'
        else:
            return f'{seconds / 604800:.1f} weeks'

    uptime = format_time_ago(time.time() - psutil.boot_time())

    if cf.get('design') == 'beauty':
        draw.text((0, y), 'uptm', font=font, fill=cf['font']['color'])
        draw.text((cf['boxmarginleft'], y), uptime, font=font, fill=cf['font']['color'])
        y += cf['linefeed']
    elif cf.get('design') == 'terminal' and term is not None:
        term.println(f'Uptime: {uptime}')
        time.sleep(2)

    logging.debug(f'Uptime: {uptime}')
    return y
