import logging
from functions import valuetocolor

def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    try:
        # Temperatur lesen
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp = int(f.read().strip()) // 1000  # °C

        font_color = cf['font']['color']
        box_left = cf['boxmarginleft']
        linefeed = cf['linefeed']
        device_width = device.width - 1

        # CPU-Temperatur-Skala (40–80°C)
        min_t = 20
        max_t = 80
        span = max_t - min_t

        # Balkenbreite berechnen
        pct = max(0, min(1, (temp - min_t) / span))
        bar_width = int((device_width - box_left) * pct)

        # Farben
        fillcolor = valuetocolor(temp, [
            [75, "Red"],
            [65, "Yellow"],
            [0,  "Green"]
        ])
        fontcolor = "Gray" if fillcolor == "Yellow" else font_color

        # Zeichnen
        draw.text((0, y), "Temp", font=font, fill=font_color)

        # Balken
        draw.rectangle(
            (box_left, y, box_left + bar_width, y + rectangle_y),
            fill=fillcolor
        )

        # Rahmen
        draw.rectangle(
            (box_left, y, device_width, y + rectangle_y),
            outline=font_color,
            width=1
        )

        # Temperaturtext
        draw.text((70, y), f"{temp}°C", font=font, fill=fontcolor)

        logging.debug("Temperature: %s°C", temp)
        return y + linefeed

    except Exception:
        logging.exception("Error rendering temperature")
        draw.text((0, y), "temp err", font=font, fill="RED")
        return y + cf.get("linefeed", 8)
