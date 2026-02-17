import socket
import logging
import time
import os
from PIL import ImageFont

def render(cf, draw, device, y, font, rectangle_y, term=None):
 try:
  hostname_font = ttffile = ttfsize = defaultfont = None
  
  hostname = str(socket.gethostname()).upper()
  if cf.get('design') == 'beauty':
#check if ttf requested and needed
   try:
    ttffile = cf['component_hostname']['font']['ttffile']
    ttfsize = cf['component_hostname']['font']['size']
    defaultfont = cf['component_hostname']['font']['default']
    if ( cf['component_hostname']['font']['default'] is False and os.path.exists(ttffile) ):
     hostname_font = ImageFont.truetype(ttffile, ttfsize) 
    else:
     pass #hostname_font = ImageFont.load_default()
   except Exception:
    logging.exception('font ' + str(ttffile) + ' size ' + str(ttfsize) + ' error')
   if not hostname_font: hostname_font = ImageFont.load_default()

   text_x = (device.width - draw.textbbox(xy=(0,0), text=hostname, font=hostname_font)[2]) / 2
   text_y = draw.textbbox(xy=(0,0), text=hostname, font=hostname_font)[3]
   draw.text((text_x, y), hostname, font=hostname_font, fill='Yellow')
   y += text_y
  elif cf.get('design') == 'terminal' and term is not None:
      term.println('Hostname: ' + hostname)
      time.sleep(2)
  logging.debug('Hostname: %s', hostname)
 except Exception:
     logging.exception('Error rendering hostname')
     draw.text((0, y), 'hostname err', font=font, fill='RED')
     y += cf.get('linefeed', 8)
 return y
