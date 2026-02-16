#!/usr/bin/python3
# Creator: Thiemo Schuff, thiemo@schuff.eu
# Source: https://github.com/Starwhooper/RPi-status-via-luna

#######################################################
#
# Prepare
#
#######################################################

#Logging Levels https://rollbar.com/blog/logging-in-python/#
#    DEBUG - Detailed information, typically of interest when diagnosing problems.
#    INFO - Confirmation of things working as expected.
#    WARNING - Indication of something unexpected or a problem in the near future e.g. 'disk space low'.
#    ERROR - A more serious problem due to which the program was unable to perform a function.
#    CRITICAL - A serious error, indicating that the program itself may not be able to continue executing.

##### check if all required packages are aviable
try:
 from luma.core.render import canvas
 from PIL import ImageFont
 from datetime import datetime, timedelta
 import json
 import logging
 import os
 import socket
 import sys
 import time
except:
 sys.exit("\033[91m {}\033[00m" .format('any needed package is not aviable. Please check README.md to check which components should be installed".'))

##### import config.json
from pathlib import Path
config_path = Path(__file__).parent / "config.json" 
try:
 with open(config_path, "r") as file: 
  cf = json.loads(file.read())
  logging.info('The configuration file ' + str(config_path) + ' loaded.')
except:
 logging.critical('The configuration file ' + config_path + ' does not exist or has incorrect content.')
 sys.exit("\033[91m {}\033[00m" .format('exit: The configuration file ' + config_path + ' does not exist or has incorrect content. Please rename the file config.json.example to config.json and change the content as required '))

##### configure logging
try:
 if cf['logging']['level'] == "debug": logging_level = logging.DEBUG
 elif cf['logging']['level'] == "info": logging_level = logging.INFO
 elif cf['logging']['level'] == "error": logging_level = logging.ERROR
 elif cf['logging']['level'] == "critical": logging_level = logging.CRITICAL
 else: logging_level = logging.WARNING
except:
 logging_level = logging.WARNING

try:
 logging_file = cf['logging']['file']
except:
 logging_file = '/var/log/rpistatusvialuma.log'
logging.getLogger("urllib3")
logging.basicConfig(
 filename=logging_file,
 level=logging_level,
 encoding='utf-8',
 format='%(asctime)s:%(levelname)s:%(message)s'
)

##### import module demo_opts from luma.examples
try:
 sys.path.append(cf['luma']['demo_opts.py']['folder'])
 from demo_opts import get_device
except:
 sys.exit("\033[91m {}\033[00m" .format('file ' + cf['luma']['demo_opts.py']['folder'] + '/demo_opts.py not found. Please check config.json or do sudo git clone https://github.com/rm-hull/luma.examples /opt/luma.examples'))
 logging.critical(format('file ' + cf['luma']['demo_opts.py']['folder'] + '/demo_opts.py not found.'))

######own functions
def valuetocolor(value,translation):
 for t in translation:
    if value >= t[0]:
        color = t[1]
        break;
 return(color)

def render_component(componentname, cf, draw, device, y, font, rectangle_y, term=None):
    """
    Lädt components.<componentname> und ruft dessen render(cf, draw, device, y, font, rectangle_y, term) auf.
    Gibt den neuen y-Wert zurück (oder den unveränderten y bei Fehler).
    """
    import importlib
    try:
        module = importlib.import_module(f'components.{componentname}')
        return module.render(cf, draw, device, y, font, rectangle_y, term)
    except ModuleNotFoundError:
        draw.text((0, y), f'MISS {componentname}', font=font, fill='RED')
        y += cf['linefeed']
        logging.error('components.%s module not found', componentname)
    except Exception as e:
        draw.text((0, y), f'{componentname} error', font=font, fill='RED')
        y += cf['linefeed']
        logging.exception('Error while rendering %s component: %s', componentname, e)
    return y
    
###### set default Font
font = None
if cf['font']['ttf'] is True:
 ttf_file = cf['font']['ttffile']
 if os.path.exists(ttf_file):
  font = ImageFont.truetype(ttf_file, cf['font']['ttfsize'])
if not font:
 font = ImageFont.load_default()
 logging.error('font ' + ttf_file + ' not found')

##### do output
def stats(device):
 global lastmessage
 global alert
 try: lastmessage
 except:
  alert='maybe restart?'
  logging.critical('maybe restart?')
  lastmessage = datetime(1977, 1, 1)

 with canvas(device, dither=True) as draw:
  if cf['design'] == 'terminal':
   term = terminal(device, font)
  global whole_y
  global offset_y

  try: whole_y
  except: whole_y = 0

  if whole_y >= device.height:
   try: offset_y = offset_y -1
   except: offset_y = 0
  else: offset_y = 0
  y=1 + offset_y

  #calculate max row height
  rectangle_y = draw.textbbox(xy=(0,0), text='AQjgp,;Ä', font=font)[3]

  #check all components
  for componentname in cf['components']:
   try:
    y = render_component(componentname, cf, draw, device, y, font, rectangle_y, term if 'term' in locals() else None)
   except:
    draw.text((0,y), 'ERR ' + componentname, font = font, fill = 'RED')
    y += cf['linefeed']
   if len(alert) >= 1:
    if cf['pushover']['messages'] == 1 and datetime.now() >= (lastmessage + timedelta(hours=1)):
     pushovermessage()    
  whole_y = y

def pushovermessage():
 import requests
 global lastmessage
 global alert
 try:
  r = requests.post('https://api.pushover.net/1/messages.json', data = {
      "token": cf['pushover']['apikey'],
      "user": cf['pushover']['userkey'],
      "html": 1,
      "priority": 1,
      "message": str(socket.gethostname()) + ' ' + alert,
      }
  )
  lastmessage = datetime.now()
  alert=''
 except:
  1
    
def main():
    while True:
        stats(device)
        time.sleep(cf['imagerefresh'])


if __name__ == '__main__':
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
