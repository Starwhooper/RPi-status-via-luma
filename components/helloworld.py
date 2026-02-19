import logging

def render(cf, draw, device, y, font, rectangle_y=None, term=None):
 try:
  outputtext = 'Hello World'   
  if cf.get('design') == 'beauty':
   draw.text((0, y), outputtext, font=font, fill='Yellow')
   y += cf['linefeed']
  elif cf.get('design') == 'terminal' and term is not None:
   term.println(outputtext)
  logging.debug('Hello World')
 except Exception:
  logging.exception('Error rendering helloworld')
  draw.text((0, y), 'hello err', font=font, fill='RED')
  y += cf.get('linefeed', 8)
 return y
