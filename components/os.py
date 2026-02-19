import logging

def load_os_info():
    try:
        # /etc/os-release lesen
        os_info = {}
        with open("/etc/os-release", "r") as f:
            for line in f:
                key, _, value = line.partition("=")
                os_info[key.strip()] = value.strip().strip('"')

        # Debian-Version lesen
        try:
            with open("/etc/debian_version", "r") as f:
                debian_version = f.read().strip()
        except Exception:
            debian_version = "unknown"

        # Ausgabe zusammenbauen
        codename = os_info.get("VERSION_CODENAME", "unknown")
        os_version_name = f"{debian_version} ({codename})"

        return os_version_name

    except Exception as e:
        logging.error(f"OS info lookup failed: {e}")
        return "unknown"

# globaler Cache
OS_VERSION_NAME = load_os_info()

def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    try:
        font_color = cf['font']['color']
        linefeed = cf['linefeed']
        box_left = cf['boxmarginleft']

        draw.text((0, y), "OS", font=font, fill=font_color)
        draw.text((box_left, y), OS_VERSION_NAME, font=font, fill=font_color)

        logging.debug(f"OS: {OS_VERSION_NAME}")
        return y + linefeed

    except Exception:
        logging.exception("Error rendering OS info")
        draw.text((0, y), "OS err", font=font, fill="RED")
        return y + cf.get("linefeed", 8)
