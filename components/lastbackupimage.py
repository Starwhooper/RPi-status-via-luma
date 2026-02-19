import glob
import os
import logging
import socket

def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    try:
        hostname = str(socket.gethostname()).lower()
        checkforlatestfile = str(cf.get('component_lastbackupimage', {}).get('checkforlatestfile', '')).replace('%HOSTNAME%', hostname)
        list_of_files = glob.glob(checkforlatestfile)
        draw.text((0, y), 'Bkp', font=font, fill=cf['font']['color'])
        if len(list_of_files) == 0:
            draw.text((cf['boxmarginleft'], y), 'missed', font=font, fill='Red')
        else:
            latest_file = max(list_of_files, key=os.path.getctime)
            latest_file_name = os.path.basename(latest_file)
            draw.text((cf['boxmarginleft'], y), latest_file_name, font=font, fill=cf['font']['color'])
        y += cf['linefeed']
    except Exception:
        logging.exception('Error rendering lastbackupimage')
        draw.text((0, y), 'bkp err', font=font, fill='RED')
        y += cf.get('linefeed', 8)
    return y
