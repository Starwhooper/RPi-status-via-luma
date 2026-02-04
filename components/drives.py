import os
import psutil
import logging
import time

def _valuetocolor(value, translation):
    for t in translation:
        if value >= t[0]:
            return t[1]
    return translation[-1][1]

def render(cf, draw, device, y, font, rectangle_y, term=None):
    try:
        drivenumber = 0
        for drive in cf.get('component_drive', {}).get('drive', []):
            if os.path.isdir(drive):
                totalsd = psutil.disk_usage(drive).total
                freesd = psutil.disk_usage(drive).free
                usagesd = totalsd - freesd
                usagesdpercent = 100 / totalsd * usagesd if totalsd > 0 else 0
                usagesd_gb = round(usagesd / (1024.0 ** 3), 1)
                string = f"{usagesd_gb}/{round(totalsd / 1024.0 ** 3,1)}GB"
                if cf.get('design') == 'beauty':
                    draw.text((0, y), 'Drv' + str(drivenumber), font=font, fill=cf['font']['color'])
                    width = (device.width - 1 - cf['boxmarginleft']) / 100 * usagesdpercent
                    fontcolor = cf['font']['color']
                    fillcolor = _valuetocolor(usagesdpercent, [[90,"Red"],[70,"Yellow"],[0,"Green"]])
                    if fillcolor == 'Yellow':
                        fontcolor = 'Grey'
                    draw.rectangle((cf['boxmarginleft'], y, cf['boxmarginleft'] + int(width), y + rectangle_y), fill=fillcolor, width=0)
                    draw.rectangle((cf['boxmarginleft'], y, device.width-1, y + rectangle_y), outline=cf['font']['color'], width=1)
                    draw.text((35, y), string, font=font, fill=fontcolor)
                    if usagesdpercent >= 80:
                        globals()['alert'] = f"<b>{drive}</b>: <font color=\"{fillcolor}\">{round(usagesdpercent)}%</font> {usagesd_gb} GB used"
                    y += cf['linefeed']
                    drivenumber += 1
                elif cf.get('design') == 'terminal' and term is not None:
                    term.println('Drive: ' + drive + ' = ' + str(string))
                    time.sleep(2)
                    drivenumber += 1
                logging.debug('Drive: %s = %s', drive, string)
            else:
                if cf.get('design') == 'beauty':
                    # fallback: write to console (original used print)
                    draw.text((0, y), f'{drive} not found', font=font, fill=cf['font']['color'])
                    y += cf['linefeed']
                elif cf.get('design') == 'terminal' and term is not None:
                    term.println('Drive: ' + drive + ' not found')
                    time.sleep(2)
                logging.debug('Drive: %s not found', drive)
    except Exception:
        logging.exception('Error rendering drives')
        draw.text((0, y), 'drives err', font=font, fill='RED')
        y += cf.get('linefeed', 8)
    return y
