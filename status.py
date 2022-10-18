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
 from PIL import ImageFont
 from datetime import datetime
 from luma.core.render import canvas
 from pathlib import Path
 import datetime
 import json
 import os
 import psutil
 import socket
 import sys
 import time
 import re
 import subprocess
 import netifaces
 import time
 import os
 import glob

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

###### set defaults
### font
try:
 if (cf['font']['default'] == True):
  ft = ImageFont.load_default()
  ft2 = ImageFont.load_default()
 elif (cf['font']['default'] == False):
  ft = ImageFont.truetype(cf['font']['ttffile'], cf['font']['size1'])
  ft2 = ImageFont.truetype(cf['font']['ttffile'], round(cf['font']['size2']))
except:
 sys.exit("\033[91m {}\033[00m" .format('exit: The configuration file ' + os.path.split(os.path.abspath(__file__))[0] + '/config.json does not provide cf[font][default], cf[font][ttffile] or cf[font][size]. Please rename the file config.json.example to config.json and change the content as required '))

##### do output
def stats(device):
    with canvas(device) as draw:
        #start at pixel 1
        y=1
        overallhight=0

        #check all components
        for componentname in cf["components"]:

            if componentname == 'currentdatetime': 
                draw.text((0,y), datetime.date.today().strftime('%a')[:2] + "," + datetime.date.today().strftime('%d.%b\'%y') + " " + time.strftime('%H:%M:%S', time.localtime()) , font=ft, fill = cf["fontcolor"])
                y=y+10

            if componentname == 'hostname':
                draw.text((0,y), str(socket.gethostname()).upper(), font=ft2, fill="yellow")
                y=y+14

            if componentname == 'temperatur':
                tFile = open('/sys/class/thermal/thermal_zone0/temp')
                temp = int(format(int(float(tFile.read())/1000),"d"))
                draw.text((0,y), "Temp", font=ft, fill = cf["fontcolor"])
                width = (cf['display']['width'] - 1 - cf["boxmarginleft"]) / (90 - 30) * (temp - 30)
                fontcolor = cf['fontcolor']
                if width < 0: width = 0
                if temp >= 70: fillcolor = 'RED'
                elif temp >= 60: fillcolor = 'YELLOW'
                else: fillcolor = 'GREEN'
                if fillcolor == 'YELLOW': fontcolor = 'GREY'
                draw.rectangle((cf["boxmarginleft"], y) + (cf["boxmarginleft"] + width, y + 10), fill=fillcolor, width=0)
                draw.rectangle((cf["boxmarginleft"], y) + (cf['display']['width']-1, y + 10), outline=cf['fontcolor'], width=1)
                draw.text((70,y), str(temp) + '°C' , font=ft, fill = fontcolor)
                y=y+10
                           
            
            if componentname == 'board':
                if 'piboardinformation' not in locals():
                 fobj = open("/sys/firmware/devicetree/base/model")
                 output = ''
                 for line in fobj:
                    output = output + line.rstrip()
                 fobj.close()
                 output = output.replace("Raspberry Pi ", "RPi ")
                 output = output.replace(" Model ", "")
                 output = output.replace("Rev ", "")
                 output = output.replace("  ", " ")
                 output = re.sub('[^a-zA-Z0-9. ]+', '', output)
                 piboardinformation = output
                draw.text((0,y), "Main" + piboardinformation, font=ft, fill = cf["fontcolor"])
                y=y+10
                
            if componentname == 'uptime':
                def formatTimeAgo(seconds):
                 if seconds < 60: return "%i seconds" % seconds
                 elif seconds < 3600: return "%i minutes" % (seconds/float(60))
                 elif seconds < (3600*24): return "%.1f hours" % (seconds/float(3600))
                 elif seconds < (3600*24*7): return "%.1f days" % (seconds/float(3600*24))
                 else: return "%.1f Weeks" % (seconds/float(3600*24*7))
                
                draw.text((0,y), "uptm" + formatTimeAgo(time.time() - psutil.boot_time()) , font=ft, fill = cf["fontcolor"])
                y=y+10
            
            if componentname == 'cpu':
                usage = int(float(psutil.cpu_percent()))
                draw.text((0,y), "CPU: ", font=ft, fill = cf["fontcolor"])
                width = (cf['display']['width'] - 1 - cf["boxmarginleft"] ) /100 * usage
                fontcolor = cf['fontcolor']
                if usage >= 80: fillcolor = 'RED'
                elif usage >= 60: fillcolor = 'YELLOW'
                else: fillcolor = 'GREEN'
                if fillcolor == 'YELLOW': fontcolor = 'GREY'
                draw.rectangle((cf["boxmarginleft"], y) + (cf["boxmarginleft"] + width, y + 10), fill=fillcolor, width=0)
                draw.rectangle((cf["boxmarginleft"], y) + (cf['display']['width']-1, y + 10), outline=cf['fontcolor'], width=1)
                draw.text((70,y), str(usage) + "%", font=ft, fill = fontcolor)
                y=y+10
                
            if componentname == 'os':
                debianversionfile = open('/etc/debian_version','r')
                debianversion = debianversionfile.read()
                draw.text((0,y), "OS : " + debianversion, font=ft, fill = cf["fontcolor"])
                y=y+10

            if componentname == 'ram':
                gpuram = int(re.sub('[^0-9]+', '', str(subprocess.check_output('/usr/bin/vcgencmd get_mem gpu|cut -d= -f2', shell=True))))
                totalmem = round(psutil.virtual_memory()[0] / 1000 ** 2) + gpuram
                usagemem = round((psutil.virtual_memory()[0] - psutil.virtual_memory()[1]) / 1000 ** 2)
                usageratemem = psutil.virtual_memory()[2]
                usagerategpuram = 100 / (totalmem + gpuram) * gpuram
                draw.text((0,y), "RAM ", font=ft, fill = cf["fontcolor"])
                width = (cf['display']['width'] - 1 - cf["boxmarginleft"]) /100 * usageratemem
                gpuwidth = (cf['display']['width'] - 1 - cf["boxmarginleft"]) /100 * usagerategpuram
                fontcolor = cf['fontcolor']
                if usageratemem >= 80: fillcolor = 'RED'
                elif usageratemem >= 60: fillcolor = 'YELLOW'
                else: fillcolor = 'GREEN'
                if fillcolor == 'YELLOW': fontcolor = 'GREY'
                draw.rectangle((cf["boxmarginleft"], y) + (cf["boxmarginleft"] + width, y + 10), fill=fillcolor, width=0)
                draw.rectangle((cf['display']['width']-1-gpuwidth, y) + (cf['display']['width']-1, y + 3), fill='RED', width=1)
                draw.rectangle((cf['display']['width']-1-gpuwidth, y + 4) + (cf['display']['width']-1, y + 6), fill='GREEN', width=1)
                draw.rectangle((cf['display']['width']-1-gpuwidth, y + 7) + (cf['display']['width']-1, y + 10), fill='BLUE', width=1)
                draw.rectangle((cf["boxmarginleft"], y) + (cf['display']['width']-1, y + 10), outline=cf['fontcolor'], width=1)
                draw.text((40,y), str(usagemem) + "+" + str(gpuram) + "/" + str(totalmem) + "MB", font=ft, fill = fontcolor)
                y=y+10

            if componentname == 'ipping':
                
                global lastping
                
              
                try: ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
                except: ip = 'noip'
               
                try: lastping
                except: lastping = 0
                
               # pinglocal = pinginternet = "offline"
                if len(cf["component_ipping"]["localpingdestination"]) >= 1: localpingdestination = cf["component_ipping"]["localpingdestination"]
                else: localpingdestination = ip[0:ip.rfind('.')] + '.1'
               
                if len(cf["component_ipping"]["remotepingdestination"]) >= 1: remotepingdestination = cf["component_ipping"]["remotepingdestination"]
                else: remotepingdestination = '8.8.8.8' #google dns
                   
                global pinglocalcolor
                global pinginternetcolor
               
                if time.time() >= lastping + cf["component_ipping"]["pingintervall"]: #Ping systems all x seconds
                 if os.system("ping -c 1 -W 1 " + localpingdestination + ">/dev/null") == 0: pinglocalcolor = 'GREEN'
                 else: pinglocalcolor = 'RED'
                 if os.system("ping -c 1 -W 1 " + remotepingdestination + ">/dev/null") == 0: pinginternetcolor = 'GREEN'
                 else: pinginternetcolor = 'RED'
                 lastping = int(time.time())
                draw.text((0,y), "IP  " + ip , fill = cf["fontcolor"])
                draw.rectangle((0, y + 11) + (int( cf['display']['width'] / cf["component_ipping"]["pingintervall"] * (int(time.time()) - lastping)), y + 12), fill="GREEN", width=1)
                draw.text((0,y), "  L", fill = pinglocalcolor)
                draw.text((0,y), "   R", fill = pinginternetcolor)
                y=y+12
               
            if componentname == 'lastbackupimage':
                hostname = str(socket.gethostname()).upper()
                try: lastimagemarqueepos
                except: lastimagemarqueepos = 0
                try: lastimagemarqueewait
                except: lastimagemarqueewait = 0
               
                checkforlatestfile = str(cf["component_lastbackupimage"]["checkforlatestfile"]).replace("%HOSTNAME%", str(hostname).lower())
                list_of_files = glob.glob(checkforlatestfile)
                if len(list_of_files) == 0:
                 draw.text((0 ,y), 'IMG ', font=ft, fill = cf["fontcolor"])
                 draw.text((0 ,y), '     missed', font=ft, fill = 'RED')
                else:
                 latest_file = max(list_of_files, key=os.path.getctime)
                 latest_file_name = os.path.basename(latest_file)
                 latest_file_name_text = 'IMG: ' + latest_file_name
                 marqueewidth, marqueewidthheight = draw.textsize(latest_file_name_text)
                 if lastimagemarqueepos <= cf['display']['width'] - marqueewidth:
                  lastimagemarqueewait = lastimagemarqueewait + 1
                 else: lastimagemarqueepos = lastimagemarqueepos - 2
                 if lastimagemarqueewait > cf["scrollingtextwait"] / cf["imagerefresh"]:
                  lastimagemarqueepos = 0
                  lastimagemarqueewait = 0
                 #scheint nicht zu scrollen!!!
                 draw.text((lastimagemarqueepos ,y), latest_file_name_text, font=ft, fill = cf["fontcolor"])
                 y=y+10
               
            if componentname == 'sd':
                 totalsd = psutil.disk_usage('/').total
                 freesd = psutil.disk_usage('/').free
                 usagesd = totalsd - freesd
                 usagesdpercent = 100 / totalsd * usagesd
                
                 if totalsd >= 17000000000: totalsd = 32
                 elif totalsd >= 9000000000: totalsd = 16
                 elif totalsd >= 5000000000: totalsd = 8
                 elif totalsd >= 3000000000: totalsd = 4
                 else: totalsd = 2
                
                 usagesd = round(usagesd / (1024.0 ** 3),1)
                 draw.text((0,y), "SD  ", font=ft, fill = cf["fontcolor"])
                 width = (cf['display']['width'] - 1 - cf["boxmarginleft"]) /100 * usagesdpercent
                 fontcolor = cf['fontcolor']
                 if usagesdpercent >= 90: fillcolor = 'RED'
                 elif usagesdpercent >= 70:
                  fillcolor = 'YELLOW'
                  fontcolor = 'GRAY'
                 elif usagesdpercent < 44 and totalsd > 4: fillcolor = 'PURPLE'
                 else: fillcolor = 'GREEN'
                 draw.rectangle((cf["boxmarginleft"], y) + (cf["boxmarginleft"] + width, y + 10), fill=fillcolor, width=0)
                 draw.rectangle((cf["boxmarginleft"], y) + (cf['display']['width']-1, y + 10), outline=cf['fontcolor'], width=1)
                 draw.text((55,y), str(usagesd) + "/" + str(totalsd) + "GB", font=ft, fill = fontcolor)

                 y=y+10

            if componentname == 'helloworld':
                 draw.text((0,y), 'Hello World' , font=ft, fill = 'YELLOW')
                 y=y+10
                 
            if componentname == 'border':
                 draw.rectangle((cf["boxmarginleft"], y) + (cf['display']['width']-1, y + 1), outline=cf['fontcolor'], width=1)
                 y=y+1
                 
            if componentname == 'version':
                v = re.sub('[^0-9\-]+', '', str(subprocess.check_output('git -C ' + os.path.split(os.path.abspath(__file__))[0] + ' show -s --format=%cd --date=format:\'%y%m%d-%H%M\'', shell=True)))
                draw.text((0,y), "Scpt" + v, font=fs, fill = cf["fontcolor"])
                y=y+10

            if componentname == 'drive':
                drivenumber = 0
                
                try: lastmessage
                except: lastmessage = 0
                
                for drive in cf["component_drive"]['drive']:
                 if os.path.isdir(drive):
                  alert = ''
                  totalsd = psutil.disk_usage(drive).total
                  freesd = psutil.disk_usage(drive).free
                  usagesd = totalsd - freesd
                  usagesdpercent = 100 / totalsd * usagesd
                
                  usagesd = round(usagesd / (1024.0 ** 3),1)
                  draw.text((0,(drivenumber+1)*y), "Drv" + str(drivenumber) , font=ft, fill = cf["fontcolor"])
                
                  width = (cf['display']['width'] - 1 - cf["boxmarginleft"]) /100 * usagesdpercent
                  fontcolor = cf['fontcolor']
                  if usagesdpercent >= 90: fillcolor = 'RED'
                  elif usagesdpercent >= 70:
                   fillcolor = 'YELLOW'
                   fontcolor = 'GRAY'
                  else: fillcolor = 'GREEN'
                  draw.rectangle((cf["boxmarginleft"], (drivenumber+1)*y) + (cf["boxmarginleft"] + width, (drivenumber+1)*y + 10), fill=fillcolor, width=0)
                  draw.rectangle((cf["boxmarginleft"], (drivenumber+1)*y) + (cf['display']['width']-1, (drivenumber+1)*y + 10), outline=cf['fontcolor'], width=1)
                  draw.text((35,(drivenumber+1)*y), str(usagesd) + "/" + str(round(totalsd / 1024.0 ** 3,1)) + "GB", font=ft, fill = fontcolor)
                  drivenumber = drivenumber + 1
                  if usagesdpercent >= 80:
                   alert = '<b>' + drive + '</b>: <font color="' + fillcolor + '">' + str(round(usagesdpercent)) + '%</font> ' + str(usagesd) + ' GB used'
                 else:
                  print('folder ' + drive + ' not found')
                 y=y+10                


def main():
    while True:
        stats(device)
        time.sleep(cf["imagerefresh"])


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
