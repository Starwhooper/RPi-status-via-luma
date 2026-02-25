import time
import os
import netifaces
import logging
import psutil

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
    #print(pingcommand)

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




def interface_exists(name: str) -> bool:
    return name in psutil.net_if_addrs()


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

            #prüfen ob NIC existiert
            if not interface_exists(interface): 
             ip = 'notexist'
            else:
                
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
            if bar_width <= 3 and ip not in ("noip", "notexist"):
                draw.text((0, y), nameonscreen + "L", font=font, fill=font_color)
                draw.text((box_left, y), f"oo {local_target}", font=font, fill=font_color)

            elif bar_width <= 5 and ip not in ("noip", "notexist"):
                draw.text((0, y), nameonscreen + " R", font=font, fill=font_color)
                draw.text((box_left, y), f"oo {remote_target}", font=font, fill=font_color)

            else:
                draw.text((0, y), nameonscreen, font=font, fill=font_color)
                draw.text((0, y), '  L', font=font, fill=local_color)
                draw.text((0, y), '   R', font=font, fill=remote_color)

                if ip == "noip":
                    draw.text((box_left, y), "no ip", font=font, fill="Yellow")
                elif ip == "notexist":
                    draw.text((box_left, y), "not exist", font=font, fill="Red")                    
                else:
                    draw.text((box_left, y), f"{ip}", font=font, fill=font_color)

            logging.debug("IP: %s %s", nameonscreen, ip)
            y += cf['linefeed'] + 2

    except Exception:
        logging.exception("Error rendering ipping")
        draw.text((0, y), "ipping err", font=font, fill="RED")
        y += cf.get("linefeed", 8)

    return y
