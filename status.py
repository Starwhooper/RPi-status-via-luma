#!/usr/bin/python3
# Creator: Thiemo Schuff
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
# from PIL import Image, ImageDraw, ImageFont
 from functions import defaultfont, render_component, pushovermessage #,valuetocolor
# import importlib
 import json
 import logging
# import os
# import requests
# import socket
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
         if cf['design'] == 'terminal': term = terminal(device, font)
         
         #scroll
         if whole_y > device.height: 
          if stayontop > 5: offset_y -= 1
          else: stayontop += 1
         else: 
          if stayonbottom > 5: 
           offset_y = 0
           stayontop = 0
           stayonbottom = 0
          else: stayonbottom += 1
         y = 0 + offset_y
       
         #calculate max row height
         rectangle_y = draw.textbbox(xy=(0,0), text='AQjgp,;Ä', font=font)[3]
       
         #check all components
         for componentname in cf['components']:
          try:
           y = render_component(componentname, cf, draw, device, y, font, rectangle_y, term if 'term' in locals() else None)
          except:
           draw.text((0,y), 'ERR ' + componentname, font = font, fill = 'RED')
           y += cf['linefeed']
          if alert:
           if cf['pushover']['messages'] == True and datetime.now() >= (lastmessagetime + timedelta(hours=1)):
            pushovermessage(cf,alert)
            lastmessagetime = datetime.now()     
            alert = ''
         whole_y = y
        time.sleep(cf['imagerefresh'])

if __name__ == '__main__':
 try:
  device = init_display()
  main(device)
 except KeyboardInterrupt:
  pass
