from __future__ import annotations
import psutil
import logging
import time

def _valuetocolor(value, translation):
    for t in translation:
        if value >= t[0]:
            return t[1]
    return translation[-1][1]

def render(cf, draw, device, y, font, rectangle_y, term=None):
    """
    Render the cpu component.
    - cf: configuration dict
    - draw: PIL drawing context
    - device: luma device
    - y: current y position (int)
    - font: PIL font
    - rectangle_y: height of a line (int)
    - term: optional terminal virtual device (for 'terminal' design)
    Returns: new y position (int)
    """
    try:
        usage = int(psutil.cpu_percent())
    except Exception:
        usage = 0

    usage_string = f'{usage}%'

    if cf.get('design') == 'beauty':
        # Draw CPU label
        draw.text((0, y), 'CPU', font=font, fill=cf['font']['color'])

        # Calculate bar width and colors
        width = (device.width - 1 - cf['boxmarginleft']) * (usage / 100)
        fill_color = _valuetocolor(usage, [[80, "Red"], [60, "Yellow"], [0, "Green"]])
        font_color = 'Grey' if fill_color == 'Yellow' else cf['font']['color']

        # Draw usage bar and outlines
        draw.rectangle(
            (cf['boxmarginleft'], y, cf['boxmarginleft'] + width, y + rectangle_y),
            fill=fill_color
        )
        draw.rectangle(
            (cf['boxmarginleft'], y, device.width - 1, y + rectangle_y),
            outline=cf['font']['color'],
            width=1
        )

        # Display usage percentage
        draw.text((70, y), usage_string, font=font, fill=font_color)
        y += cf['linefeed']

    elif cf.get('design') == 'terminal' and term is not None:
        term.println(f'CPU usage: {usage_string}')
        time.sleep(2)

    logging.debug(f'CPU usage: {usage_string}')
    return y
