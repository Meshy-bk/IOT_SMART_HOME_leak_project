# Smart Water Leak Detection System
# Uses public MQTT broker (HiveMQ) for demo purposes.
# Each component runs in its own terminal.

import time, json
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883

CMD_TOPIC = "leak/cmd/valve"           # OPEN / CLOSE / AUTO
STATUS_TOPIC = "leak/valve/status"

valve_open = True
auto_mode = True

def publish_status(client):
    status_msg = json.dumps({
        "mode": "AUTO" if auto_mode else "MANUAL",
        "state": "OPEN" if valve_open else "CLOSED"
    })
    client.publish(STATUS_TOPIC, status_msg, retain=True)
    print("Valve status published:", status_msg)

def on_message(client, userdata, msg):
    global valve_open, auto_mode
    if msg.topic == CMD_TOPIC:
        cmd = msg.payload.decode().strip().upper()
        if cmd == "OPEN":
            valve_open = True
            auto_mode = False
            print("Valve forced OPEN (manual)")
        elif cmd == "CLOSE":
            valve_open = False
            auto_mode = False
            print("Valve forced CLOSE (manual)")
        elif cmd == "AUTO":
            auto_mode = True
            print("Valve back to AUTO mode")
        publish_status(client)

def main():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.subscribe(CMD_TOPIC)

    print("🚰 Valve relay running")
    publish_status(client)

    while True:
        client.loop(timeout=0.1)
        time.sleep(0.2)

if __name__ == "__main__":
    main()
