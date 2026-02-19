import time
import psutil
import logging

def format_time_ago(seconds):
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes"
    elif seconds < 86400:
        return f"{seconds / 3600:.1f} hours"
    elif seconds < 604800:
        return f"{seconds / 86400:.1f} days"
    else:
        return f"{seconds / 604800:.1f} weeks"


def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    try:
        font_color = cf['font']['color']
        box_left = cf['boxmarginleft']
        linefeed = cf['linefeed']

        # Uptime berechnen
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_str = format_time_ago(uptime_seconds)

        # Zeichnen
        draw.text((0, y), "uptm", font=font, fill=font_color)
        draw.text((box_left, y), uptime_str, font=font, fill=font_color)

        logging.debug(f"Uptime: {uptime_str}")
        return y + linefeed

    except Exception:
        logging.exception("Error rendering uptime")
        draw.text((0, y), "uptm err", font=font, fill="RED")
        return y + cf.get("linefeed", 8)
