#!/usr/bin/python3
# Creator: Thiemo Schuff, thiemo@schuff.eu
# Source: https://github.com/Starwhooper/RPi-status-via-luna

#######################################################
#
# Prepare
#
#######################################################

##### check if all required packages are aviable
try:
 from luma.core.render import canvas
 from pathlib import Path
 from PIL import ImageFont
 import datetime
 import glob
 import json
 import netifaces
 import os
 import psutil
 import re
 import socket
 import subprocess
 import sys
 import time
except:
 sys.exit("\033[91m {}\033[00m" .format('any needed package is not aviable. Please check README.md to check which components shopuld be installed via pip3".'))

##### ensure that only one instance is running at the same time
runninginstances = 0
for p in psutil.process_iter():
 if len(p.cmdline()) == 2:
  if p.cmdline()[0] == '/usr/bin/python3':
   if p.cmdline()[1] == os.path.abspath(__file__):
    runninginstances = runninginstances + 1
if runninginstances >= 2:
 sys.exit("\033[91m {}\033[00m" .format('exit: is already running'))
 
##### import config.json
try:
 with open(os.path.split(os.path.abspath(__file__))[0] + '/config.json','r') as file:
  cf = json.loads(file.read())
except:
 sys.exit("\033[91m {}\033[00m" .format('exit: The configuration file ' + os.path.split(os.path.abspath(__file__))[0] + '/config.json does not exist or has incorrect content. Please rename the file config.json.example to config.json and change the content as required '))

##### import module demo_opts
try:
 sys.path.append(cf['luma']['demo_opts.py']['folder'])
 from demo_opts import get_device
except:
 sys.exit("\033[91m {}\033[00m" .format('file ' + cf['luma']['demo_opts.py']['folder'] + '/demo_opts.py not found. Please check config.json or do sudo git clone https://github.com/rm-hull/luma.examples /opt/luma.examples'))

######own functions
def valuetocolor(value,translation):
 for t in translation:
    if value >= t[0]:
        color = t[1]
        break;
 return(color)

###### set defaults
###alerts
#lastmessage=0 
#alert=''

if cf['font']['ttf'] == True:
 font = ImageFont.truetype(cf['font']['ttffile'], cf['font']['ttfsize'])
else:
 font = ImageFont.load_default()


##### do output
def stats(device):
 lastmessage=0 
 alert=''
 with canvas(device) as draw:
  #reset values
  y=1
#  overallhight=0

  rectangle_y = draw.textbbox(xy=(0,0), text='Aj', font=font)[3]
  
  #check all components
  for componentname in cf['components']:
   if componentname == 'currentdatetime': 
       draw.text((0,y), datetime.date.today().strftime('%a')[:2] + ',' + datetime.date.today().strftime('%d.%b\'%y') + ' ' + time.strftime('%H:%M:%S', time.localtime()), font = font, fill = cf['font']['color'])
       y=y+cf['linefeed']
  
   elif componentname == 'hostname':
       ### font
       try:
        if (cf['component_hostname']['font']['default'] == True):
         hostname_font = ImageFont.load_default()
        elif (cf['component_hostname']['font']['default'] == False):
         hostname_font = ImageFont.truetype(cf['component_hostname']['font']['ttffile'], cf['component_hostname']['font']['size'])
       except:
        sys.exit("\033[91m {}\033[00m" .format('exit: The configuration file ' + os.path.split(os.path.abspath(__file__))[0] + '/config.json does not provide cf[font][default], cf[font][ttffile] or cf[font][size]. Please rename the file config.json.example to config.json and change the content as required '))

       text_x = (device.width - draw.textbbox(xy=(0,0), text=str(socket.gethostname()).upper(), font=hostname_font)[2]) / 2
       text_y = draw.textbbox(xy=(0,0), text=str(socket.gethostname()).upper(), font=hostname_font)[3]
       draw.text((text_x,y), str(socket.gethostname()).upper(), font=hostname_font, fill='Yellow')
       y=y+text_y
  
   elif componentname == 'temperatur':
       tFile = open('/sys/class/thermal/thermal_zone0/temp')
       temp = int(format(int(float(tFile.read())/1000),'d'))
       draw.text((0,y), 'Temp', font = font, fill = cf['font']['color'])
       width = (device.width - 1 - cf['boxmarginleft']) / (90 - 30) * (temp - 30)
       fontcolor = cf['font']['color']
       if width < 0: width = 0
       fillcolor = valuetocolor(temp,[[70,"Red"],[60,"Yellow"],[0,"Green"]])
       if fillcolor == 'Yellow': fontcolor = 'Gray'
       draw.rectangle((cf['boxmarginleft'], y) + (cf['boxmarginleft'] + width, y + rectangle_y), fill=fillcolor, width=0)
       draw.rectangle((cf['boxmarginleft'], y) + (device.width-1, y + rectangle_y), outline=cf['font']['color'], width=1)
       draw.text((70,y), str(temp) + '°C' , font = font, fill = fontcolor)
       y=y+cf['linefeed']
                  
   elif componentname == 'board':
       if 'piboardinformation' not in locals():
        fobj = open('/sys/firmware/devicetree/base/model')
        output = ''
        for line in fobj:
           output = output + line.rstrip()
        fobj.close()
        output = output.replace('Raspberry Pi ', 'RPi ')
        output = output.replace(' Model ', '')
        output = output.replace(' Plus', '+')
        output = output.replace('Rev ', '')
        output = output.replace('  ', ' ')
        output = re.sub('[^a-zA-Z0-9.+ ]+', '', output)
        piboardinformation = output
       draw.text((0,y), 'Brd', font = font, fill = cf['font']['color'])
       draw.text((cf['boxmarginleft'],y), piboardinformation, font = font, fill = cf['font']['color'])
       y=y+cf['linefeed']
       
   elif componentname == 'uptime':
       def formatTimeAgo(seconds):
        if seconds < 60: return '%i seconds' % seconds
        elif seconds < 3600: return '%i minutes' % (seconds/float(60))
        elif seconds < (3600*24): return '%.1f hours' % (seconds/float(3600))
        elif seconds < (3600*24*7): return '%.1f days' % (seconds/float(3600*24))
        else: return '%.1f Weeks' % (seconds/float(3600*24*7))
       
       draw.text((0,y), 'uptm', font = font, fill = cf['font']['color'])
       draw.text((cf['boxmarginleft'],y), formatTimeAgo(time.time() - psutil.boot_time()), font = font, fill = cf['font']['color'])
       y=y+cf['linefeed']
   
   elif componentname == 'cpu':
       usage = int(float(psutil.cpu_percent()))
       draw.text((0,y), 'CPU', font = font, fill = cf['font']['color'])
       width = (device.width - 1 - cf['boxmarginleft'] ) /100 * usage
       fontcolor = cf['font']['color']
       fillcolor = valuetocolor(usage,[[80,"Red"],[60,"Yellow"],[0,"Green"]])
       if fillcolor == 'Yellow': fontcolor = 'Grey'
       draw.rectangle((cf['boxmarginleft'], y) + (cf['boxmarginleft'] + width, y + rectangle_y), fill=fillcolor, width=0)
       draw.rectangle((cf['boxmarginleft'], y) + (device.width-1, y + rectangle_y), outline=cf['font']['color'], width=1)
       draw.text((70,y), str(usage) + '%', font = font, fill = fontcolor)
       y=y+cf['linefeed']
       
   elif componentname == 'os':
       debianversionfile = open('/etc/debian_version','r')
       debianversion = debianversionfile.read()
       draw.text((0,y), 'OS', font = font, fill = cf['font']['color'])
       draw.text((cf['boxmarginleft'],y), debianversion, font = font, fill = cf['font']['color'])
       y=y+cf['linefeed']
  
   elif componentname == 'ram':
       gpuram = int(re.sub('[^0-9]+', '', str(subprocess.check_output('/usr/bin/vcgencmd get_mem gpu|cut -d= -f2', shell=True))))
       totalmem = round(psutil.virtual_memory()[0] / 1000 ** 2) + gpuram
       usagemem = round((psutil.virtual_memory()[0] - psutil.virtual_memory()[1]) / 1000 ** 2)
       usageratemem = psutil.virtual_memory()[2]
       usagerategpuram = 100 / (totalmem + gpuram) * gpuram
       draw.text((0,y), 'RAM', font = font, fill = cf['font']['color'])
       width = (device.width - 1 - cf['boxmarginleft']) /100 * usageratemem
       gpuwidth = (device.width - 1 - cf['boxmarginleft']) /100 * usagerategpuram
       fontcolor = cf['font']['color']
       fillcolor = valuetocolor(usageratemem,[[80,"Red"],[60,"Yellow"],[0,"Green"]])
       if fillcolor == 'Yellow': fontcolor = 'Grey'
       draw.rectangle((cf['boxmarginleft'], y) + (cf['boxmarginleft'] + width, y + rectangle_y), fill=fillcolor, width=0)
       draw.rectangle((device.width-1-gpuwidth, y) + (device.width-1, y + rectangle_y/3*1), fill='Red', width=1)
       draw.rectangle((device.width-1-gpuwidth, y + 4) + (device.width-1, y + rectangle_y/3*2), fill='Green', width=1)
       draw.rectangle((device.width-1-gpuwidth, y + 7) + (device.width-1, y + rectangle_y), fill='Blue', width=1)
       draw.rectangle((cf['boxmarginleft'], y) + (device.width-1, y + rectangle_y), outline=cf['font']['color'], width=1)
       draw.text((40,y), str(usagemem) + '+' + str(gpuram) + '/' + str(totalmem) + 'MB', font = font, fill = fontcolor)
       y=y+cf['linefeed']
  
   elif componentname == 'ipping':
       global lastping
     
       try: ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
       except: ip = 'noip'
      
       try: lastping
       except: lastping = 0
       
      # pinglocal = pinginternet = "offline"
       if len(cf['component_ipping']['localpingdestination']) >= 1: localpingdestination = cf['component_ipping']['localpingdestination']
       else: localpingdestination = ip[0:ip.rfind('.')] + '.1' #local ip ends with 1, as example 192.168.178.1 or 10.0.0.1
      
       if len(cf['component_ipping']['remotepingdestination']) >= 1: remotepingdestination = cf['component_ipping']['remotepingdestination']
       else: remotepingdestination = '8.8.8.8' #google dns
          
       global pinglocalcolor
       global pinginternetcolor
      
       if time.time() >= lastping + cf['component_ipping']['pingintervall']: #Ping systems all x seconds
        if os.system('ping -c 1 -W 1 ' + localpingdestination + '>/dev/null') == 0: pinglocalcolor = 'Green'
        else: pinglocalcolor = 'Red'
        if os.system('ping -c 1 -W 1 ' + remotepingdestination + '>/dev/null') == 0: pinginternetcolor = 'Green'
        else: pinginternetcolor = 'Red'
        lastping = int(time.time())
       draw.text((0,y), 'IP', font = font, fill = cf['font']['color'])
       draw.text((0,y), '  L', font = font, fill = pinglocalcolor)
       draw.text((0,y), '   R', font = font, fill = pinginternetcolor)
       draw.text((cf['boxmarginleft'],y), ip , font = font, fill = cf['font']['color'])
       draw.rectangle((0, y + 11) + (int( device.width / cf['component_ipping']['pingintervall'] * (int(time.time()) - lastping)), y + rectangle_y + 2), fill='Green', width=1)
       y=y+cf['linefeed']+2
      
   elif componentname == 'lastbackupimage':
       hostname = str(socket.gethostname()).upper()
       try: lastimagemarqueepos
       except: lastimagemarqueepos = 0
       try: lastimagemarqueewait
       except: lastimagemarqueewait = 0
      
       checkforlatestfile = str(cf['component_lastbackupimage']['checkforlatestfile']).replace('%HOSTNAME%', str(hostname).lower())
       list_of_files = glob.glob(checkforlatestfile)
       draw.text((0 ,y), 'Bkp', font = font, fill = cf['font']['color'])
       if len(list_of_files) == 0:
        draw.text((cf['boxmarginleft'],y), 'missed', font = font, fill = 'Red')
       else:
        latest_file = max(list_of_files, key=os.path.getctime)
        latest_file_name = os.path.basename(latest_file)
        draw.text((cf['boxmarginleft'],y), latest_file_name, font = font, fill = cf['font']['color'])
       y=y+cf['linefeed']
      
   elif componentname == 'helloworld':
        draw.text((0,y), 'Hello World', font = font, fill = 'Yellow')
        y=y+cf['linefeed']
        
   elif componentname == 'version':
       draw.text((0,y), 'Scpt', font = font, fill = cf['font']['color'])
       draw.text((cf['boxmarginleft'],y), re.sub('[^0-9\-]+', '', str(subprocess.check_output('git -C ' + os.path.split(os.path.abspath(__file__))[0] + ' show -s --format=%cd --date=format:\'%y%m%d-%H%M\'', shell=True))), font = font, fill = cf['font']['color'])
       y=y+cf['linefeed']
  
   elif componentname == 'drives':
       drivenumber = 0
       
#       try: lastmessage
#       except: lastmessage = 0
       
       for drive in cf['component_drive']['drive']:
        if os.path.isdir(drive):
#         alert = ''
         totalsd = psutil.disk_usage(drive).total
         freesd = psutil.disk_usage(drive).free
         usagesd = totalsd - freesd
         usagesdpercent = 100 / totalsd * usagesd
       
         usagesd = round(usagesd / (1024.0 ** 3),1)
         draw.text((0,(drivenumber+1)*y), 'Drv' + str(drivenumber), font = font, fill = cf['font']['color'])
       
         width = (device.width - 1 - cf['boxmarginleft']) /100 * usagesdpercent
         fontcolor = cf['font']['color']
         fillcolor = valuetocolor(usagesdpercent,[[90,"Red"],[70,"Yellow"],[0,"Green"]])
         if fillcolor == 'Yellow': fontcolor = 'Grey'
         draw.rectangle((cf['boxmarginleft'], (drivenumber+1)*y) + (cf['boxmarginleft'] + width, (drivenumber+1)*y + rectangle_y), fill=fillcolor, width=0)
         draw.rectangle((cf['boxmarginleft'], (drivenumber+1)*y) + (device.width-1, (drivenumber+1)*y + rectangle_y), outline=cf['font']['color'], width=1)
         draw.text((35,(drivenumber+1)*y), str(usagesd) + '/' + str(round(totalsd / 1024.0 ** 3,1)) + 'GB', font = font, fill = fontcolor)
         drivenumber = drivenumber + 1
         if usagesdpercent >= 80:
          alert = '<b>' + drive + '</b>: <font color="' + fillcolor + '">' + str(round(usagesdpercent)) + '%</font> ' + str(usagesd) + ' GB used'
        else:
         print('folder ' + drive + ' not found')
        y=y+cf['linefeed']                
        
   else:
        draw.text((0,y), 'unknown component', font = font, fill = 'RED')
        y=y+cf['linefeed']
   
   if len(alert) >= 1:
    if cf['pushover']['messages'] == 1 and time.time() >= lastmessage + 60 * 60 * 24:
     import requests
     r = requests.post('https://api.pushover.net/1/messages.json', data = {
         "token": cf['pushover']['apikey'],
         "user": cf['pushover']['userkey'],
         "html": 1,
         "priority": 1,
         "message": hostname + ' ' + alert,
         }
     ,
     files = {
      "attachment": ("image.png", open(str(cf['savescreen']['destination']).replace('%HOSTNAME%', str(socket.gethostname()).lower()), 'rb'), 'image/png')
     }
     )
     lastmessage = time.time()
     alert=''
   


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
