import re
import subprocess
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
    Render the RAM component and return the new y position.
    Signatur: render(cf, draw, device, y, font, rectangle_y, term=None) -> int
    """
    # GPU-RAM ermitteln (vcgencmd), falls nicht vorhanden -> 0
    try:
        out = subprocess.check_output('/usr/bin/vcgencmd get_mem gpu|cut -d= -f2', shell=True, stderr=subprocess.DEVNULL)
        gpuram = int(re.sub(r'[^0-9]+', '', out.decode()))
    except Exception:
        gpuram = 0

    vm = psutil.virtual_memory()
    totalmem = round(vm.total / (1000 ** 2)) + gpuram
    usagemem = round((vm.total - vm.available) / (1000 ** 2))
    usageratemem = vm.percent
    # Verhalten wie im Originalcode nachbilden
    try:
        usagerategpuram = 100 / (totalmem + gpuram) * gpuram if (totalmem + gpuram) > 0 else 0
    except Exception:
        usagerategpuram = 0

    string = f"{usagemem}+{gpuram}/{totalmem}MB"

    if cf.get('design') == 'beauty':
        try:
            draw.text((0, y), 'RAM', font=font, fill=cf['font']['color'])

            width = (device.width - 1 - cf['boxmarginleft']) / 100 * usageratemem
            gpuwidth = (device.width - 1 - cf['boxmarginleft']) / 100 * usagerategpuram

            fontcolor = cf['font']['color']
            fillcolor = _valuetocolor(usageratemem, [[80, "Red"], [60, "Yellow"], [0, "Green"]])
            if fillcolor == 'Yellow':
                fontcolor = 'Grey'

            # Haupt-Usage-Balken
            draw.rectangle(
                (cf['boxmarginleft'], y, cf['boxmarginleft'] + int(width), y + int(rectangle_y)),
                fill=fillcolor, width=0
            )

            # GPU-Balken rechts als drei farbige Segmente (wie im Original)
            gw = int(gpuwidth)
            if gw > 0:
                band_h = max(1, int(rectangle_y / 3))
                right_x0 = device.width - 1 - gw
                # obere Band (rot)
                draw.rectangle((right_x0, y, device.width - 1, y + band_h), fill='Red', width=0)
                # mittleres Band (grün)
                draw.rectangle((right_x0, y + band_h, device.width - 1, y + 2 * band_h), fill='Green', width=0)
                # unteres Band (blau)
                draw.rectangle((right_x0, y + 2 * band_h, device.width - 1, y + int(rectangle_y)), fill='Blue', width=0)

            # Rahmen
            draw.rectangle((cf['boxmarginleft'], y, device.width - 1, y + int(rectangle_y)), outline=cf['font']['color'], width=1)

            # Text
            draw.text((40, y), string, font=font, fill=fontcolor)
            y += cf['linefeed']
        except Exception:
            logging.exception('Error drawing RAM component')
            draw.text((0, y), 'RAM draw err', font=font, fill='RED')
            y += cf.get('linefeed', 8)

    elif cf.get('design') == 'terminal' and term is not None:
        term.println('RAM: ' + string)
        time.sleep(2)

    logging.debug('RAM: %s', string)
    return y
