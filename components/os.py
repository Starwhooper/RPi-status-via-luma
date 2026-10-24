import logging
import struct

def load_os_info():
    try:
        # /etc/os-release lesen
        os_info = {}
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if "=" in line:
                        key, _, value = line.partition("=")
                        os_info[key.strip()] = value.strip().strip('"')
        except Exception:
            pass

        debian_version = os_info.get("DEBIAN_VERSION_FULL", "").strip()
        if not debian_version:
            try:
                with open("/etc/debian_version", "r") as f:
                    debian_version = f.read().strip()
            except Exception:
                debian_version = "unknown"

        codename = os_info.get("VERSION_CODENAME", "").strip()

        if not codename:
         codename = "?"

        system_bits = f"{struct.calcsize('P') * 8}B" 

        if codename != "?" and codename in debian_version.lower():
            os_version_name = f"{debian_version} {system_bits}"
        else:
            os_version_name = f"{debian_version} ({codename}) {system_bits}"

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
