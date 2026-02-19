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
 from datetime import datetime, timedelta
 from luma.core.render import canvas
 from luma.core.interface.serial import spi
 from luma.lcd.device import st7735
 from pathlib import Path
 from functions import defaultfont, render_component, pushovermessage, scrollimage #,valuetocolor
 import json
 import logging
 import sys
 import time
except:
 sys.exit("\033[91m {}\033[00m" .format('any needed package is not aviable. Please check README.md to check which components should be installed".'))

##### import config.json
config_path = Path(__file__).parent / "config.json" 
try:
 with open(config_path, "r") as file: 
  cf = json.loads(file.read())
except:
 sys.exit("\033[91m {}\033[00m" .format('exit: The configuration file ' + config_path + ' does not exist or has incorrect content. Please rename the file config.json.example to config.json and change the content as required '))

##### configure logging
try:
 logging_level = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING, "error": logging.ERROR, "critical": logging.CRITICAL, }.get(cf['logging']['level'], logging.WARNING)
except:
 logging_level = logging.WARNING
try:
 logging_file = cf['logging']['file']
except:
 logging_file = '/var/log/rpistatusvialuma.log'
logging.getLogger("urllib3")
logging.basicConfig(filename=logging_file, level=logging_level, encoding='utf-8', format='%(asctime)s:%(levelname)s:%(message)s')

# global definieren
lastmessagetime = datetime(1977, 1, 1)
alert=''

def init_display():
    serial = spi(
        port=0,
        device=0,
        gpio_DC=23,
        gpio_RST=24,
        bus_speed_hz=32000000
    )
    device = st7735(
        serial,
        width=160,
        height=128,
        gpio_LIGHT=18,
        active_low=False,
        rotate=3
    )
    return device

def main(device):
    toplimit = cf.get('image', {}).get('toplimit', 0)
    bottomlimit = cf.get('image', {}).get('bottomlimit', 0)
    imagerefresh = cf.get('image', {}).get('refresh', 0)
    imagesavepath = cf.get('image', {}).get('savepath', 0)
    lastsave = datetime(1977, 1, 1)
    
    while True:
        global lastmessagetime
        global alert
        global whole_y
        global offset_y
        global stayontop
        global stayonbottom
        
        if (lastmessagetime == datetime(1977, 1, 1)): alert='maybe restart?'
        whole_y = globals().get("whole_y", 0) #whole_y = 0 wenn bisher ungenutzt
        stayontop = globals().get("stayontop", 0) #whole_y = 0 wenn bisher ungenutzt
        stayonbottom = globals().get("stayonbottom", 0) #whole_y = 0 wenn bisher ungenutzt
        offset_y = globals().get("offset_y", 0) #whole_y = 0 wenn bisher ungenutzt
       
        font = defaultfont(cf)
        with canvas(device, dither=True) as draw:
         offset_y, stayontop, stayonbottom, y = scrollimage( whole_y, device.height, offset_y, stayontop, stayonbottom, toplimit, bottomlimit )
       
         #calculate max row height
         rectangle_y = draw.textbbox(xy=(0,0), text='AQjgp,;Ä', font=font)[3]
       
         #check all components
         for componentname in cf['components']:
          try:
           y = render_component(componentname, cf, draw, device, y, font, rectangle_y, term=None)
          except:
           draw.text((0,y), 'ERR ' + componentname, font = font, fill = 'RED')
           y += cf['linefeed']
          if alert:
           if cf['pushover']['messages'] == True and datetime.now() >= (lastmessagetime + timedelta(hours=1)):
            pushovermessage(cf,alert)
            lastmessagetime = datetime.now()     
            alert = ''
         whole_y = y
         
         # --- Bild speichern alle 5 Minuten --- 
         if (datetime.now() >= lastsave + timedelta(minutes=5) and offset_y == 0): 
             filename = datetime.now().strftime(imagesavepath) 
             img = draw._image.copy() 
             img.save(filename) 
             lastsave = datetime.now()         
  
        time.sleep(imagerefresh)

if __name__ == '__main__':
 try:
  device = init_display()
  main(device)
 except KeyboardInterrupt:
  pass
