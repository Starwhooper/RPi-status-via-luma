#!/usr/bin/python3
# Creator: Thiemo Schuff, thiemo@schuff.eu
# Source: https://github.com/Starwhooper/RPi-status-on-luna

#######################################################
#
# Prepare
#
#######################################################

##### check if all required packages are aviable
try:
# from /opt/luma.examples/examples/demo_opts.py import get_device
 from luma.core.render import canvas
 from PIL import ImageFont
 from pathlib import Path
# from PIL import Image
# from PIL import ImageDraw
 import json
 import os
 import psutil
 import socket
 import sys
 from datetime import datetime
 import time
# import glob
except:
 sys.exit('any needed package is not aviable. Please check README.md to check which components shopuld be installed via pip3".')

sys.path.append('/opt/luma.examples/examples')
from demo_opts import get_device

##### ensure that only one instance is running at the same time
runninginstances = 0
for p in psutil.process_iter():
 if len(p.cmdline()) == 2:
  if p.cmdline()[0] == '/usr/bin/python3':
   if p.cmdline()[1] == os.path.abspath(__file__):
    runninginstances = runninginstances + 1
if runninginstances >= 2:
 sys.exit('exit: is already running') 
 
##### import config.json
try:
 with open(os.path.split(os.path.abspath(__file__))[0] + '/config.json','r') as file:
  cf = json.loads(file.read())
except:
 sys.exit('exit: The configuration file ' + os.path.split(os.path.abspath(__file__))[0] + '/config.json does not exist or has incorrect content. Please rename the file config.json.example to config.json and change the content as required ')

###### set defaults
### font
try:
 if (cf['font']['default'] == True):
  ft = ImageFont.load_default()   
 elif (cf['font']['default'] == False):
  ft = ImageFont.truetype(cf['font']['ttffile'], cf['font']['size'])
except:
 sys.exit('exit: The configuration file ' + os.path.split(os.path.abspath(__file__))[0] + '/config.json does not provide cf[font][default], cf[font][ttffile] or cf[font][size]. Please rename the file config.json.example to config.json and change the content as required ')

def stats(device):
 


    with canvas(device) as draw:
        y=0
        for componentname in cf["components"]:
            if componentname == 'hostname':
                draw.text((0,y), str(socket.gethostname()).upper(), font=ft, fill="red")
                y=y+10
            if componentname == 'cpu':
                draw.text((0, y), str(float(psutil.cpu_percent())), font=ft, fill="white")
                y=y+10
            if componentname == 'ram':
                draw.text((0, y), str(round((psutil.virtual_memory()[0] - psutil.virtual_memory()[1]) / 1000 ** 2)), font=ft, fill="white")
                y=y+10
            if componentname == 'sd':
                draw.text((0, y), str(psutil.disk_usage('/').total- psutil.disk_usage('/').free), font=ft, fill="white")
                y=y+10

def main():
    while True:
        stats(device)
        time.sleep(1)


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
