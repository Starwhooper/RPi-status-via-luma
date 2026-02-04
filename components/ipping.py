import time
import os
import netifaces
import logging

def render(cf, draw, device, y, font, rectangle_y, term=None):
    try:
        try:
            lastping = globals()['lastping']
        except KeyError:
            lastping = 0
            globals()['lastping'] = lastping

        for interface in netifaces.interfaces():
            if interface == 'lo':
                continue
            try:
                ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
            except Exception:
                ip = 'noip'
            if cf.get('design') == 'beauty':
                localpingdestination = cf.get('component_ipping', {}).get('localpingdestination') or (ip[:ip.rfind('.')] + '.1' if ip != 'noip' else '')
                remotepingdestination = cf.get('component_ipping', {}).get('remotepingdestination') or '8.8.8.8'
                pingintervall = cf.get('component_ipping', {}).get('pingintervall', 30)
                try:
                    lastping = globals().get('lastping', 0)
                    if time.time() >= lastping + pingintervall:
                        if os.system(f'ping -c 1 -W 1 -I {interface} {localpingdestination} >/dev/null') == 0:
                            globals()['pinglocalcolor'] = 'Green'
                        else:
                            globals()['pinglocalcolor'] = 'Red'
                        if os.system(f'ping -c 1 -W 1 -I {interface} {remotepingdestination} >/dev/null') == 0:
                            globals()['pinginternetcolor'] = 'Green'
                        else:
                            globals()['pinginternetcolor'] = 'Red'
                        globals()['lastping'] = int(time.time())
                except Exception:
                    globals()['pinglocalcolor'] = globals().get('pinglocalcolor', 'Red')
                    globals()['pinginternetcolor'] = globals().get('pinginternetcolor', 'Red')
                draw.text((0, y), 'IP', font=font, fill=cf['font']['color'])
                draw.text((0, y), '  L', font=font, fill=globals().get('pinglocalcolor', 'Red'))
                draw.text((0, y), '   R', font=font, fill=globals().get('pinginternetcolor', 'Red'))
                # try to show interface name and ip
                draw.text((cf['boxmarginleft'], y), '  ' + ip, font=font, fill=cf['font']['color'])
                # progress-like rectangle
                pingintervall = max(1, cf.get('component_ipping', {}).get('pingintervall', 30))
                elapsed = int(time.time()) - globals().get('lastping', 0)
                barw = int(device.width / pingintervall * elapsed)
                draw.rectangle((0, y + 11, min(device.width-1, barw), y + rectangle_y + 2), fill='Green', width=1)
                y += cf['linefeed'] + 2
            elif cf.get('design') == 'terminal' and term is not None:
                term.println('IP: ' + interface + ' ' + ip)
                time.sleep(2)
            logging.debug('IP: %s %s', interface, ip)
    except Exception:
        logging.exception('Error rendering ipping')
        draw.text((0, y), 'ipping err', font=font, fill='RED')
        y += cf.get('linefeed', 8)
    return y
