import sqlite3
import logging
import time

def render(cf, draw, device, y, font, rectangle_y, term=None):
    try:
        dbfile = cf.get('component_pihole', {}).get('dbfile')
        if not dbfile:
            raise ValueError('no dbfile configured for pihole')
        con = sqlite3.connect(dbfile)
        cur = con.cursor()
        if cf.get('component_pihole', {}).get('showlastblockeddomain', False):
            try:
                cur.execute("SELECT domain FROM queries WHERE status NOT IN (" + cf['component_pihole'].get('allowedstatus','') + ") and timestamp >= strftime('%s','now','-5 minute') ORDER BY timestamp DESC LIMIT 1;")
                row = cur.fetchone()
                if row is not None:
                    blockeddomain = row[0]
                    shortenblockeddomain = ".".join(blockeddomain.split(".")[-3:])
                    if len(shortenblockeddomain) > 17:
                        shortenblockeddomain = "_" + shortenblockeddomain[-16:]
                else:
                    shortenblockeddomain = blockeddomain = '---'
            except Exception:
                shortenblockeddomain = blockeddomain = "DB ERROR"
                logging.warning('Pi-Hole block domain unknown')
            if cf.get('design') == 'beauty':
                draw.text((0, y), 'blkd', font=font, fill=cf['font']['color'])
                draw.text((cf['boxmarginleft'], y), shortenblockeddomain, font=font, fill=cf['font']['color'])
                y += cf['linefeed']
            elif cf.get('design') == 'terminal' and term is not None:
                term.println('Pi-Hole blocked:' + blockeddomain)
                time.sleep(2)
            logging.debug('Pi-Hole last blocked domain: %s', blockeddomain)

        if cf.get('component_pihole', {}).get('showblockedlast24h', False):
            try:
                cur.execute("SELECT COUNT(id) FROM queries WHERE status NOT IN (" + cf['component_pihole'].get('allowedstatus','') + ") and timestamp >= strftime('%s','now','-" + str(cf['component_pihole'].get('lastblockedhours',24)) + " hour') ;")
                row = cur.fetchone()
                blocked = row[0] if row is not None else 0
            except Exception:
                blocked = 0
                logging.warning('Pi-Hole found no blocked domain')
            try:
                cur.execute("SELECT COUNT(id) FROM queries WHERE timestamp >= strftime('%s','now','-" + str(cf['component_pihole'].get('lastblockedhours',24)) + " hour');")
                row = cur.fetchone()
                allq = row[0] if row is not None else 0
            except Exception:
                allq = 0
                logging.warning('Pi-Hole found no allowed and blocked domain')
            rate = round(blocked / allq * 100) if allq > 0 else 0
            string = f"{blocked} ({rate}%) in {cf['component_pihole'].get('lastblockedhours',24)}h"
            if cf.get('design') == 'beauty':
                draw.text((0, y), 'blkc', font=font, fill=cf['font']['color'])
                draw.text((cf['boxmarginleft'], y), string, font=font, fill=cf['font']['color'])
                y += cf['linefeed']
            elif cf.get('design') == 'terminal' and term is not None:
                term.println(string)
                time.sleep(2)
            logging.debug('Pi-Hole block rate: %s', string)
        con.close()
    except Exception:
        logging.exception('Error rendering pihole')
        draw.text((0, y), 'pihole err', font=font, fill='RED')
        y += cf.get('linefeed', 8)
    return y
