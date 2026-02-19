import platform
import logging

def get_kernel_short():
    try:
        full = platform.release()              # z.B. "6.1.0-18-rpi-v8"
        short = full.split('-')[0]             # → "6.1.0"
        return full, short
    except Exception as e:
        logging.error(f"Kernel lookup failed: {e}")
        return "unknown", "unknown"

# globale Cache-Variablen
KERNEL_FULL, KERNEL_SHORT = get_kernel_short()

def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    try:
        font_color = cf['font']['color']
        linefeed = cf['linefeed']
        box_left = cf['boxmarginleft']

        draw.text((0, y), "krnl", font=font, fill=font_color)
        draw.text((box_left, y), KERNEL_SHORT, font=font, fill=font_color)

        logging.debug("Kernel: %s", KERNEL_FULL)
        return y + linefeed

    except Exception:
        logging.exception("Error rendering kernelversion")
        draw.text((0, y), "krnl err", font=font, fill="RED")
        return y + cf.get("linefeed", 8)
