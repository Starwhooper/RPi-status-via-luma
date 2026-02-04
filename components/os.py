import logging

def render(cf, draw, device, y, font, rectangle_y, term=None):
        def get_os_release():
            os_info = {}
            with open("/etc/os-release", "r") as file:
                for line in file:
                    key, _, value = line.partition("=")
                    os_info[key.strip()] = value.strip().strip('"')
            return os_info

        def get_debian_version():
            with open('/etc/debian_version', 'r') as file:
                return file.read().strip()


        os_info = get_os_release()
        debian_version = get_debian_version()

        os_version_name = f"{debian_version} ({os_info.get('VERSION_CODENAME', 'unknown')})"

        if cf['design'] == 'beauty':
            draw.text((0, y), 'OS', font=font, fill=cf['font']['color'])
            draw.text((cf['boxmarginleft'], y), os_version_name, font=font, fill=cf['font']['color'])
            y += cf['linefeed']
        elif cf['design'] == 'terminal':
            term.println(f"OS: {os_version_name}")
            time.sleep(2)

        logging.debug(f"OS: {os_version_name}")
        return y
