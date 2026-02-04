import logging
import time

def _valuetocolor(value, translation):
    for t in translation:
        if value >= t[0]:
            return t[1]
    return translation[-1][1]

def render(cf, draw, device, y, font, rectangle_y, term=None):
    try:
        with open('/sys/class/thermal/thermal_zone0/temp') as tFile:
            temp = int(int(float(tFile.read())/1000))
        if cf.get('design') == 'beauty':
            draw.text((0, y), 'Temp', font=font, fill=cf['font']['color'])
            width = (device.width - 1 - cf['boxmarginleft']) / (90 - 30) * (temp - 30)
            fontcolor = cf['font']['color']
            if width < 0:
                width = 0
            fillcolor = _valuetocolor(temp, [[70,"Red"],[60,"Yellow"],[0,"Green"]])
            if fillcolor == 'Yellow':
                fontcolor = 'Gray'
            draw.rectangle((cf['boxmarginleft'], y, cf['boxmarginleft'] + int(width), y + rectangle_y), fill=fillcolor, width=0)
            draw.rectangle((cf['boxmarginleft'], y, device.width-1, y + rectangle_y), outline=cf['font']['color'], width=1)
            draw.text((70, y), str(temp) + '°C', font=font, fill=fontcolor)
            y += cf['linefeed']
        elif cf.get('design') == 'terminal' and term is not None:
            term.println('Temperature: ' + str(temp) + '°C')
            time.sleep(2)
        logging.debug('Temperature: %s°C', temp)
    except Exception:
        logging.exception('Error rendering temperatur')
        draw.text((0, y), 'temp err', font=font, fill='RED')
        y += cf.get('linefeed', 8)
    return y
