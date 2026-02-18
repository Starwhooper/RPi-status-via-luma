from __future__ import annotations
import psutil
import logging

def _valuetocolor(value, translation):
    for threshold, color in translation:
        if value >= threshold:
            return color
    return translation[-1][1]


def render(cf, draw, device, y, font, rectangle_y, term=None):
    """
    Render the CPU component.
    """
    # --- CPU usage lesen ---
    try:
        usage = int(psutil.cpu_percent())
    except Exception:
        logging.exception("Error reading CPU usage")
        usage = 0

    usage_string = f"{usage}%"

    # --- Farben & Layout aus Config robust lesen ---
    font_color_default = cf.get("font", {}).get("color", "white")
    box_margin_left = cf.get("boxmarginleft", 0)
    linefeed = cf.get("linefeed", 8)

    # --- CPU Label ---
    draw.text((0, y), "CPU", font=font, fill=font_color_default)

    # --- Balkenbreite berechnen ---
    max_width = device.width - 1 - box_margin_left
    bar_width = max_width * (usage / 100)

    # --- Farbe abhängig vom Wert ---
    fill_color = _valuetocolor(
        usage,
        [
            (80, "Red"),
            (60, "Yellow"),
            (0,  "Green"),
        ]
    )

    # Schriftfarbe anpassen, wenn Gelb schlecht lesbar wäre
    font_color = "Grey" if fill_color == "Yellow" else font_color_default

    # --- Balken zeichnen ---
    draw.rectangle(
        (box_margin_left, y, box_margin_left + bar_width, y + rectangle_y),
        fill=fill_color
    )

    # Rahmen
    draw.rectangle(
        (box_margin_left, y, device.width - 1, y + rectangle_y),
        outline=font_color_default,
        width=1
    )

    # --- Prozentzahl ---
    draw.text((70, y), usage_string, font=font, fill=font_color)

    y += linefeed

    logging.debug("CPU usage: %s", usage_string)
    return y
