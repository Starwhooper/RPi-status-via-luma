import logging
import time
import paho.mqtt.client as mqtt

# globaler Speicher für den letzten MQTT-Payload
last_payload = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe("$SYS/broker/load/messages/publish/1min")
    else:
        print("Verbindungsfehler:", rc)

def on_message(client, userdata, msg):
    global last_payload
    last_payload = msg.payload.decode()  # Payload speichern
    client.disconnect()  # nach der ersten Nachricht beenden




def render(cf, draw, device, y, font, rectangle_y, term=None):
    global last_payload
    
    client = mqtt.Client()
    client.username_pw_set(cf['component_mqttstatus']['mqttuser'], cf['component_mqttstatus']['mqttpassword'])
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect("localhost", 1883, 60)
    client.loop_forever()
    
    try:
        display_text = last_payload if last_payload else "no MQTT data"
        
        if cf.get('design') == 'beauty':
            draw.text((0, y), 'MQTT', font=font, fill=cf['font']['color'])
            draw.text((cf['boxmarginleft'], y), display_text + ' clients', font=font, fill=cf['font']['color'])
            y += cf['linefeed']
        elif cf.get('design') == 'terminal' and term is not None:
            term.println('MQTT ' + display_text + ' pub/min')
            time.sleep(2)
        logging.debug('MQTT: ' + display_text + ' pub/min')
    except Exception:
        logging.exception('Error rendering MQTT payload')
        draw.text((0, y), 'render err', font=font, fill='RED')
        y += cf.get('linefeed', 8)
    return y

