# Smart Water Leak Detection System
# Uses public MQTT broker (HiveMQ) for demo purposes.
# Each component runs in its own terminal.

import paho.mqtt.client as mqtt
import time, random, json

BROKER = "broker.hivemq.com"
PORT = 1883

LEAK_TOPIC = "leak/sensor/leak"
SAMPLE_INTERVAL = 3  # seconds

leak_state = 0  # 0 = no leak, 1 = leak

def main():
    global leak_state
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    print("💧 Leak sensor running...")

    while True:
        # Demo behavior: sometimes leak happens, sometimes it stops
        if leak_state == 0 and random.random() < 0.05:
            leak_state = 1
        elif leak_state == 1 and random.random() < 0.15:
            leak_state = 0

        payload = json.dumps({"leak": leak_state})
        client.publish(LEAK_TOPIC, payload)
        print("Sent leak:", payload)
        time.sleep(SAMPLE_INTERVAL)

if __name__ == "__main__":
    main()
