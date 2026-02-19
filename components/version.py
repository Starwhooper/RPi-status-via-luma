import os
import logging
import subprocess

def render(cf, draw, device, y, font, rectangle_y=None, term=None):
    string = GIT_VERSION  # aus Cache

    draw.text((0, y), "Scpt", font=font, fill=cf['font']['color'])
    draw.text((cf['boxmarginleft'], y), string, font=font, fill=cf['font']['color'])
    y += cf['linefeed']

    logging.debug("Skript Version: " + string)
    return y

def get_git_version():
    try:
        repo_path = os.path.dirname(os.path.abspath(__file__))
        result = subprocess.check_output(
            ["git", "-C", repo_path, "show", "-s", "--format=%cd", "--date=format:%y%m%d-%H%M"],
            stderr=subprocess.STDOUT
        )
        return result.decode("utf-8").strip()
    except Exception as e:
        logging.error(f"Git version lookup failed: {e}")
        return "unknown"

# globale Variable
GIT_VERSION = get_git_version()
