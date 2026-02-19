####provide a color to a value. As example you provide 100, you will get red
#def valuetocolor(value,translation):
# for t in translation:
#    if value >= t[0]:
#        color = t[1]
#        break;
# return(color)

####try to use a ttf, otherwise default font
def defaultfont(cf):
 from PIL import ImageFont
 font = None
 if cf['font']['ttf'] is True:
  ttf_file = cf['font']['ttffile']
  if os.path.exists(ttf_file):
   font = ImageFont.truetype(ttf_file, cf['font']['ttfsize'])
  else:
   logging.error('font ' + ttf_file + ' not found')
 if not font:
  font = ImageFont.load_default()
 return font

#####request graphic feedback from component
def render_component(componentname, cf, draw, device, y, font, rectangle_y, term=None):
 from luma.core.render import canvas
 import importlib
 import logging
#    Lädt components.<componentname> und ruft dessen render(cf, draw, device, y, font, rectangle_y, term) auf.     Gibt den neuen y-Wert zurück (oder den unveränderten y bei Fehler).
 try:
  module = importlib.import_module(f'components.{componentname}')
  return module.render(cf, draw, device, y, font, rectangle_y, term=None)
 except ModuleNotFoundError:
  draw.text((0, y), f'MISS {componentname}', font=font, fill='RED')
  y += cf['linefeed']
  logging.error('components.%s module not found', componentname)
 except Exception as e:
  draw.text((0, y), f'{componentname} error', font=font, fill='RED')
  y += cf['linefeed']
  logging.exception('Error while rendering %s component: %s', componentname, e)
 return y

#####send pushover message
def pushovermessage(cf,alert):
 import requests
 import socket
 try:
  r = requests.post('https://api.pushover.net/1/messages.json', data = {
      "token": cf['pushover']['apikey'],
      "user": cf['pushover']['userkey'],
      "html": 1,
      "priority": 1,
      "message": str(socket.gethostname()) + ' ' + alert,
      }
  )
 except:
  1
  
#scroll
def scrollimage(whole_y, device_height, offset_y, stayontop, stayonbottom, toplimit, bottomlimit):
    # Wenn der Inhalt höher ist als das Display → nach oben scrollen
    if whole_y > device_height:
        if stayontop > toplimit:
            offset_y -= 1
        else:
            stayontop += 1
    else:
        # Wenn unten angekommen → Reset
        if stayonbottom > bottomlimit:
            offset_y = 0
            stayontop = 0
            stayonbottom = 0
        else:
            stayonbottom += 1

    y = offset_y
    return offset_y, stayontop, stayonbottom, y
