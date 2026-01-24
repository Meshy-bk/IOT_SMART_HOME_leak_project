# Smart Water Leak Detection System
# Uses public MQTT broker (HiveMQ) for demo purposes.
# Each component runs in its own terminal.

import time, json
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883

CMD_TOPIC = "leak/cmd/siren"           # ON / OFF / AUTO
STATUS_TOPIC = "leak/siren/status"
STATE_TOPIC = "leak/state"             # NORMAL/WARNING/ALARM

siren_on = False
auto_mode = True
system_state = "NORMAL"

def publish_status(client):
    status_msg = json.dumps({
        "mode": "AUTO" if auto_mode else "MANUAL",
        "state": "ON" if siren_on else "OFF"
    })
    client.publish(STATUS_TOPIC, status_msg, retain=True)
    print("Siren status published:", status_msg)

def on_message(client, userdata, msg):
    global siren_on, auto_mode, system_state
    if msg.topic == CMD_TOPIC:
        cmd = msg.payload.decode().strip().upper()
        if cmd == "ON":
            siren_on = True
            auto_mode = False
            print("Siren forced ON (manual)")
        elif cmd == "OFF":
            siren_on = False
            auto_mode = False
            print("Siren forced OFF (manual)")
        elif cmd == "AUTO":
            auto_mode = True
            print("Siren back to AUTO mode")
        publish_status(client)

    elif msg.topic == STATE_TOPIC:
        system_state = (msg.payload.decode().strip().upper() or "NORMAL")

def main():
    global siren_on
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.subscribe(CMD_TOPIC)
    client.subscribe(STATE_TOPIC)

    print("🚨 Siren relay running")
    publish_status(client)

    while True:
        client.loop(timeout=0.1)

        # Simple AUTO behavior: siren ON only when state==ALARM
        if auto_mode:
            desired = (system_state == "ALARM")
            if desired != siren_on:
                siren_on = desired
                print("Siren AUTO -> {} (state={})".format("ON" if siren_on else "OFF", system_state))
                publish_status(client)

        time.sleep(0.5)

if __name__ == "__main__":
    main()
