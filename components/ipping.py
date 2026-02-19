import time
import os
import netifaces
import logging

def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    try:
        # Konfiguration
        cfg = cf.get('component_ipping', {})
        ping_interval = max(1, cfg.get('pingintervall', 30))
        font_color = cf['font']['color']
        box_left = cf['boxmarginleft']

        # globale Ping-Zeit initialisieren
        lastping = globals().get('lastping', 0)

        # Interfaces durchgehen
        for interface in netifaces.interfaces():
            if interface == 'lo':
                continue

            # IP-Adresse holen
            try:
                ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
            except Exception:
                ip = 'noip'

            # Ping-Ziele bestimmen
            local_dst = cfg.get('localpingdestination') or (
                ip.rsplit('.', 1)[0] + '.1' if ip != 'noip' else ''
            )
            remote_dst = cfg.get('remotepingdestination', '8.8.8.8')

            # Pings nur alle X Sekunden ausführen
            now = time.time()
            if now >= lastping + ping_interval:
                # Lokaler Ping
                globals()['pinglocalcolor'] = (
                    'Green' if os.system(f'ping -c 1 -W 1 -I {interface} {local_dst} >/dev/null 2>&1') == 0
                    else 'Red'
                )

                # Internet-Ping
                globals()['pinginternetcolor'] = (
                    'Green' if os.system(f'ping -c 1 -W 1 -I {interface} {remote_dst} >/dev/null 2>&1') == 0
                    else 'Red'
                )

                globals()['lastping'] = int(now)
                lastping = globals()['lastping']

            # Farben holen
            local_color = globals().get('pinglocalcolor', 'Red')
            remote_color = globals().get('pinginternetcolor', 'Red')

            # Anzeige
            draw.text((0, y), 'IP', font=font, fill=font_color)
            draw.text((0, y), '  L', font=font, fill=local_color)
            draw.text((0, y), '   R', font=font, fill=remote_color)

            # IP anzeigen
            draw.text((box_left, y), f"  {ip}", font=font, fill=font_color)

            # Fortschrittsbalken für Ping-Intervall
            elapsed = int(now) - lastping
            bar_width = int(device.width / ping_interval * elapsed)
            bar_width = min(device.width - 1, bar_width)

            draw.rectangle(
                (0, y + 11, bar_width, y + rectangle_y + 2),
                fill='Green'
            )

            logging.debug("IP: %s %s", interface, ip)
            y += cf['linefeed'] + 2

    except Exception:
        logging.exception("Error rendering ipping")
        draw.text((0, y), "ipping err", font=font, fill="RED")
        y += cf.get("linefeed", 8)

    return y
