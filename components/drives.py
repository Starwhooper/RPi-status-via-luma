import os
import psutil
import logging
from functions import valuetocolor

def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    try:
        drives = cf.get('component_drive', {}).get('drive', [])
        box_left = cf['boxmarginleft']
        font_color_default = cf['font']['color']
        linefeed = cf['linefeed']

        for idx, drive in enumerate(drives):
            if os.path.isdir(drive):
                # Disk usage nur EINMAL abfragen
                usage = psutil.disk_usage(drive)

                total = usage.total
                used = usage.used
                free = usage.free

                # Prozent + GB-Werte
                percent = (used / total * 100) if total > 0 else 0
                used_gb = round(used / (1024**3), 1)
                total_gb = round(total / (1024**3), 1)

                # Text
                string = f"{used_gb}/{total_gb}GB"

                # Farben
                fillcolor = valuetocolor(percent, [[90, "Red"], [70, "Yellow"], [0, "Green"]])
                fontcolor = "Grey" if fillcolor == "Yellow" else font_color_default

                # Balkenbreite
                bar_width = int((device.width - 1 - box_left) * (percent / 100))

                # Zeichnen
                draw.text((0, y), f"Drv{idx}", font=font, fill=font_color_default)
                draw.rectangle(
                    (box_left, y, box_left + bar_width, y + rectangle_y),
                    fill=fillcolor
                )
                draw.rectangle(
                    (box_left, y, device.width - 1, y + rectangle_y),
                    outline=font_color_default,
                    width=1
                )
                draw.text((35, y), string, font=font, fill=fontcolor)

                # Alert
                if percent >= 80:
                    globals()['alert'] = (
                        f"<b>{drive}</b>: <font color=\"{fillcolor}\">"
                        f"{round(percent)}%</font> {used_gb} GB used"
                    )

                logging.debug("Drive: %s = %s", drive, string)
                y += linefeed

            else:
                # Drive existiert nicht
                draw.text((0, y), f"{drive} not found", font=font, fill=font_color_default)
                logging.debug("Drive: %s not found", drive)
                y += linefeed

    except Exception:
        logging.exception("Error rendering drives")
        draw.text((0, y), "drives err", font=font, fill="RED")
        y += cf.get("linefeed", 8)

    return y
