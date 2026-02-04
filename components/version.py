import os
import re
import time
import logging
import subprocess

def render(cf, draw, device, y, font, rectangle_y, term=None):
        string = re.sub('[^0-9\-]+', '', str(subprocess.check_output('git -C ' + os.path.split(os.path.abspath(__file__))[0] + ' show -s --format=%cd --date=format:\'%y%m%d-%H%M\'', shell=True)))
        if cf['design'] == 'beauty':
         draw.text((0,y), 'Scpt', font = font, fill = cf['font']['color'])
         draw.text((cf['boxmarginleft'],y), string, font = font, fill = cf['font']['color'])
         y += cf['linefeed']
        if cf['design'] == 'terminal':
         term.println('Version: ' + string)
         time.sleep(2)
        logging.debug('Skript Version: ' + string)
        return y
