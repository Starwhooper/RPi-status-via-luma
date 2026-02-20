import time
import os
import netifaces
import logging


def short_name(interface):
    """
    Kürzt Interface-Namen:
    eth0  -> e0
    wlan1 -> w1
    enp3s0 -> e0 (nimmt ersten Buchstaben + letzte Ziffer)
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
    - 'noconnect'  → Netzwerkkabel nicht eingesteckt
    - 'ok'         → Ping erfolgreich
    - 'fail'       → Ping fehlgeschlagen
    """

    # 1) Kein Kabel → noconnect
    if not link_status(interface):
        return "noconnect"

    # 2) Kabel steckt, aber keine IP → noip
    if ip == "noip":
        return "noip"

    # 3) Normales Ping
    result = os.system(f'ping -c 1 -W 1 -I {interface} {target} >/dev/null 2>&1')
    return "ok" if result == 0 else "fail"


def status_color(status):
    """Farbzuordnung für Status."""
    if status == "ok":
        return "Green"
    if status == "fail":
        return "Red"
    if status == "noip":
        return "Yellow"
    if status == "noconnect":
        return "Orange"
    return "Red"


def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    try:
        cfg = cf.get('component_ipping', {})
        ping_interval = max(1, cfg.get('pingintervall', 30))
        font_color = cf['font']['color']
        box_left = cf['boxmarginleft']

        lastping = globals().get('lastping', 0)
        now = time.time()

        devices = cfg.get("devices", [])

        for dev in devices:
            interface = dev.get("interface", "")
            name = short_name(interface)

            local_target = dev.get("local", "")
            remote_target = dev.get("remote", "")

            # IP-Adresse holen
            try:
                ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
            except Exception:
                ip = 'noip'

            # Pings nur alle X Sekunden ausführen
            if now >= lastping + ping_interval:

                # Lokaler Ping
                local_status = ping_status(interface, local_target, ip) if local_target else "fail"

                # Remote Ping
                remote_status = ping_status(interface, remote_target, ip) if remote_target else "fail"

                globals()[f'ping_local_{name}'] = status_color(local_status)
                globals()[f'ping_remote_{name}'] = status_color(remote_status)

                globals()['lastping'] = int(now)
                lastping = globals()['lastping']

            # Farben holen
            local_color = globals().get(f'ping_local_{name}', 'Red')
            remote_color = globals().get(f'ping_remote_{name}', 'Red')

            # Anzeige
            draw.text((0, y), name, font=font, fill=font_color)
            draw.text((0, y), '  L', font=font, fill=local_color)
            draw.text((0, y), '   R', font=font, fill=remote_color)

            # IP oder "no ip" anzeigen
            if ip == "noip":
                draw.text((box_left, y), "no ip", font=font, fill="Yellow")
            else:
                draw.text((box_left, y), f"{ip}", font=font, fill=font_color)

            # Fortschrittsbalken
            elapsed = int(now) - lastping
            bar_width = int(device.width / ping_interval * elapsed)
            bar_width = min(device.width - 1, bar_width)

            draw.rectangle(
                (0, y + 11, bar_width, y + rectangle_y + 2),
                fill='Green'
            )

            logging.debug("IP: %s %s", name, ip)
            y += cf['linefeed'] + 2

    except Exception:
        logging.exception("Error rendering ipping")
        draw.text((0, y), "ipping err", font=font, fill="RED")
        y += cf.get("linefeed", 8)

    return y
