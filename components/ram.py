import subprocess
import re
import logging

def load_gpu_ram():
    try:
        out = subprocess.check_output(
            "/usr/bin/vcgencmd get_mem gpu",
            shell=True,
            stderr=subprocess.DEVNULL
        )
        # Beispiel: "gpu=76M"
        return int(re.sub(r"[^0-9]", "", out.decode()))
    except Exception as e:
        logging.error(f"GPU RAM lookup failed: {e}")
        return 0

GPU_RAM_MB = load_gpu_ram()

import psutil
import logging
from functions import valuetocolor

def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    try:
        font_color = cf['font']['color']
        box_left = cf['boxmarginleft']
        linefeed = cf['linefeed']
        device_width = device.width - 1

        # RAM-Daten
        vm = psutil.virtual_memory()
        used_mb = round((vm.total - vm.available) / (1024**2))
        total_mb = round(vm.total / (1024**2))
        percent = vm.percent

        # GPU-RAM aus Cache
        gpu_mb = GPU_RAM_MB

        # Anzeige-String
        string = f"{used_mb}+{gpu_mb}/{total_mb}MB"

        # Farben
        fillcolor = valuetocolor(percent, [[80, "Red"], [60, "Yellow"], [0, "Green"]])
        fontcolor = "Grey" if fillcolor == "Yellow" else font_color

        # Balkenbreite
        bar_width = int((device_width - box_left) * (percent / 100))

        # Zeichnen
        draw.text((0, y), "RAM", font=font, fill=font_color)

        # RAM-Balken
        draw.rectangle(
            (box_left, y, box_left + bar_width, y + rectangle_y),
            fill=fillcolor
        )

        # GPU-Balken (nur wenn GPU-RAM > 0)
        if gpu_mb > 0:
            gpu_width = int((device_width - box_left) * (gpu_mb / (total_mb + gpu_mb)))
            if gpu_width > 0:
                band_h = max(1, rectangle_y // 3)
                x0 = device_width - gpu_width

                draw.rectangle((x0, y, device_width, y + band_h), fill="Red")
                draw.rectangle((x0, y + band_h, device_width, y + 2*band_h), fill="Green")
                draw.rectangle((x0, y + 2*band_h, device_width, y + rectangle_y), fill="Blue")

        # Rahmen
        draw.rectangle(
            (box_left, y, device_width, y + rectangle_y),
            outline=font_color,
            width=1
        )

        # Text
        draw.text((40, y), string, font=font, fill=fontcolor)

        logging.debug("RAM: %s", string)
        return y + linefeed

    except Exception:
        logging.exception("Error drawing RAM component")
        draw.text((0, y), "RAM draw err", font=font, fill="RED")
        return y + cf.get("linefeed", 8)
