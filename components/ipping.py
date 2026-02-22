#import time
#import os
#import netifaces
#import logging
#
#
#def short_name(interface):
#    """
#    Kürzt Interface-Namen:
#    eth0  -> e0
#    wlan1 -> w1
#    (nimmt ersten Buchstaben + letzte Ziffer)
#    """
#    letters = ''.join([c for c in interface if c.isalpha()])
#    digits = ''.join([c for c in interface if c.isdigit()])
#
#    if not letters:
#        letters = interface[0]
#
#    if not digits:
#        digits = "0"
#
#    return letters[0] + digits[-1]
#
#
#def link_status(interface):
#    """Gibt True zurück, wenn ein Netzwerkkabel steckt, sonst False."""
#    try:
#        path = f"/sys/class/net/{interface}/carrier"
#        with open(path, "r") as f:
#            return f.read().strip() == "1"
#    except Exception:
#        return False
#
#
#def ping_status(interface, target, ip):
#    """
#    Gibt zurück:
#    - 'noip'       → Interface hat keine IP
#    - 'noconnect'  → Netzwerkkabel nicht eingesteckt
#    - 'ok'         → Ping erfolgreich
#    - 'fail'       → Ping fehlgeschlagen
#    """
#
#    # 2) Kabel steckt, aber keine IP → noip
#    if ip == "noip":
#        return "noip"
#
#    # 3) Normales Ping
#    pingcommand = f'ping -c 1 -W 1 -I {interface} {target} >/dev/null 2>&1'
#    result = os.system(pingcommand)
#    print(pingcommand)
#    #result = os.system(f'ping -c 1 -W 1 -I {interface} {target} >/dev/null 2>&1')
#    #logging.debug(pingcommand)
#    return "ok" if result == 0 else "fail"
#
#
#def status_color(status):
#    """Farbzuordnung für Status."""
#    if status == "ok":
#        return "Green"
#    if status == "fail":
#        return "Red"
#    if status == "noip":
#        return "Yellow"
##    if status == "noconnect":
##        return "Orange"
#    return "Red"
#
#
#def render(cf, draw, device, y, font, rectangle_y=None, term=None):
#    try:
#        cfg = cf.get('component_ipping', {})
#        ping_interval = max(1, cfg.get('pingintervall', 30))
#        font_color = cf.get('font', {}).get('color', 'white')
#        box_left = cf['boxmarginleft']
#
#        lastping = globals().get('lastping', 0)
#        now = time.time()
#
#        devices = cfg.get("devices", [])
#
#        for dev in devices:
#            interface = dev.get("interface", "")
#            name = short_name(interface)
#
#            local_target = dev.get("local", "")
#            remote_target = dev.get("remote", "")
#
#            # IP-Adresse holen
#            try:
#                ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
#            except Exception:
#                ip = 'noip'
#
#            if local_target == "" and ip != "noip":
#                parts = ip.split(".") 
#                parts[-1] = "1" 
#                local_target = ".".join(parts)
#                
#            if remote_target == "" and ip != "noip":
#                remote_target = '86.54.11.1' #DNS4EU
#
#            # Pings nur alle X Sekunden ausführen
#            if now >= lastping + ping_interval:
#
#                # Lokaler Ping
#                local_status = ping_status(interface, local_target, ip) if local_target else "fail"
#
#                # Remote Ping
#                remote_status = ping_status(interface, remote_target, ip) if remote_target else "fail"
#
#                globals()[f'ping_local_{name}'] = status_color(local_status)
#                globals()[f'ping_remote_{name}'] = status_color(remote_status)
#
#                globals()['lastping'] = int(now)
#                lastping = globals()['lastping']
#
#            # Farben holen
#            local_color = globals().get(f'ping_local_{name}', 'Red')
#            remote_color = globals().get(f'ping_remote_{name}', 'Red')
#
#            # Fortschrittsbalken
#            elapsed = int(now) - lastping
#            bar_width = int(device.width / ping_interval * elapsed)
#            bar_width = min(device.width - 1, bar_width)
#
#            draw.rectangle(
#                (0, y + 11, bar_width, y + rectangle_y + 2),
#                fill='Green'
#            )
#            
#            if bar_width <= 3 and ip != "noip":
#                draw.text((0, y), name + "L", font=font, fill=font_color)
#                draw.text((box_left, y), f"oo {local_target}", font=font, fill=font_color)
#            elif bar_width <= 5 and ip != "noip":
#                draw.text((0, y), name + " R", font=font, fill=font_color)
#                draw.text((box_left, y), f"oo {remote_target}", font=font, fill=font_color)
#            else:
#                # Anzeige
#                draw.text((0, y), name, font=font, fill=font_color)
#                draw.text((0, y), '  L', font=font, fill=local_color)
#                draw.text((0, y), '   R', font=font, fill=remote_color)
#    
#                # IP oder "no ip" anzeigen
#                if ip == "noip":
#                    draw.text((box_left, y), "no ip", font=font, fill="Yellow")
#                else:
#                    draw.text((box_left, y), f"{ip}", font=font, fill=font_color)
#
#
#            logging.debug("IP: %s %s", name, ip)
#            y += cf['linefeed'] + 2
#
#    except Exception:
#        logging.exception("Error rendering ipping")
#        draw.text((0, y), "ipping err", font=font, fill="RED")
#        y += cf.get("linefeed", 8)
#
#    return y

import time
import os
import netifaces
import logging

# lastPing pro Gerät (Key = Interface-Name)
lastping = {}


def short_name(interface):
    """
    Kürzt Interface-Namen:
    eth0  -> e0
    wlan1 -> w1
    (nimmt ersten Buchstaben + letzte Ziffer)
    """
    letters = ''.join([c for c in interface if c.isalpha()])
    digits = ''.join([c for c in interface if c.isdigit()])

    if not letters:
        letters = interface[0]

    if not digits:
        digits = "0"

    return letters[0] + digits[-1]


def link_status(interface):
    """Gibt True zurück, wenn ein Netzwerkkabel steckt, sonst False."""
    try:
        path = f"/sys/class/net/{interface}/carrier"
        with open(path, "r") as f:
            return f.read().strip() == "1"
    except Exception:
        return False


def ping_status(interface, target, ip):
    """
    Gibt zurück:
    - 'noip'       → Interface hat keine IP
    - 'ok'         → Ping erfolgreich
    - 'fail'       → Ping fehlgeschlagen
    """

    if ip == "noip":
        return "noip"

    pingcommand = f'ping -c 1 -W 1 -I {interface} {target} >/dev/null 2>&1'
    result = os.system(pingcommand)
    print(pingcommand)

    return "ok" if result == 0 else "fail"


def status_color(status):
    """Farbzuordnung für Status."""
    if status == "ok":
        return "Green"
    if status == "fail":
        return "Red"
    if status == "noip":
        return "Yellow"
    return "Red"


def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    try:
        cfg = cf.get('component_ipping', {})
        ping_interval = max(1, cfg.get('pingintervall', 30))
        font_color = cf.get('font', {}).get('color', 'white')
        box_left = cf['boxmarginleft']

        devices = cfg.get("devices", [])
        now = time.time()

        for dev in devices:

            # Eindeutiger Key pro Gerät
            dev_key = dev.get("interface", "")

            # Falls noch kein lastPing existiert → initialisieren
            if dev_key not in lastping:
                lastping[dev_key] = 0

            interface = dev.get("interface", "")
            nameonscreen = short_name(interface)

            local_target = dev.get("local", "")
            remote_target = dev.get("remote", "")

            # IP-Adresse holen
            try:
                ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
            except Exception:
                ip = 'noip'

            # Lokales Ziel automatisch bestimmen
            if local_target == "" and ip != "noip":
                parts = ip.split(".")
                parts[-1] = "1"
                local_target = ".".join(parts)

            # Remote Ziel Standardwert
            if remote_target == "" and ip != "noip":
                remote_target = '86.54.11.1'

            # Prüfen ob Ping fällig ist
            if now >= lastping[dev_key] + ping_interval:

                local_status = ping_status(interface, local_target, ip) if local_target else "fail"
                remote_status = ping_status(interface, remote_target, ip) if remote_target else "fail"

                globals()[f'ping_local_{nameonscreen}'] = status_color(local_status)
                globals()[f'ping_remote_{nameonscreen}'] = status_color(remote_status)

                lastping[dev_key] = int(now)

            # Farben holen
            local_color = globals().get(f'ping_local_{nameonscreen}', 'Red')
            remote_color = globals().get(f'ping_remote_{nameonscreen}', 'Red')

            # Fortschrittsbalken pro Gerät
            elapsed = int(now) - lastping[dev_key]
            bar_width = int(device.width / ping_interval * elapsed)
            bar_width = min(device.width - 1, bar_width)

            draw.rectangle(
                (0, y + 11, bar_width, y + rectangle_y + 2),
                fill='Green'
            )

            # Anzeige abhängig vom Fortschritt
            if bar_width <= 3 and ip != "noip":
                draw.text((0, y), nameonscreen + "L", font=font, fill=font_color)
                draw.text((box_left, y), f"oo {local_target}", font=font, fill=font_color)

            elif bar_width <= 5 and ip != "noip":
                draw.text((0, y), nameonscreen + " R", font=font, fill=font_color)
                draw.text((box_left, y), f"oo {remote_target}", font=font, fill=font_color)

            else:
                draw.text((0, y), nameonscreen, font=font, fill=font_color)
                draw.text((0, y), '  L', font=font, fill=local_color)
                draw.text((0, y), '   R', font=font, fill=remote_color)

                if ip == "noip":
                    draw.text((box_left, y), "no ip", font=font, fill="Yellow")
                else:
                    draw.text((box_left, y), f"{ip}", font=font, fill=font_color)

            logging.debug("IP: %s %s", nameonscreen, ip)
            y += cf['linefeed'] + 2

    except Exception:
        logging.exception("Error rendering ipping")
        draw.text((0, y), "ipping err", font=font, fill="RED")
        y += cf.get("linefeed", 8)

    return y
