# Smart Water Leak Detection System
# Uses public MQTT broker (HiveMQ) for demo purposes.
# Each component runs in its own terminal.

import paho.mqtt.client as mqtt
import time, random, json

BROKER = "broker.hivemq.com"
PORT = 1883

FLOW_TOPIC = "leak/sensor/flow"
LEAK_TOPIC = "leak/sensor/leak"
SAMPLE_INTERVAL = 3

current_flow = 12.0
leak_state = 0

def on_message(client, userdata, msg):
    global leak_state
    if msg.topic == LEAK_TOPIC:
        try:
            leak_state = int(json.loads(msg.payload.decode()).get("leak", 0))
        except:
            leak_state = 0

def main():
    global current_flow
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.subscribe(LEAK_TOPIC)
    client.loop_start()
    print("📈 Flow sensor running...")

    while True:
        if leak_state == 0:
            current_flow += random.uniform(-2.0, 2.0)
            current_flow = max(0, min(30, current_flow))
        else:
            # Leak scenario: abnormal high flow spikes
            current_flow += random.uniform(5.0, 12.0)
            current_flow = max(0, min(100, current_flow))

        payload = json.dumps({"flow": round(current_flow, 2)})
        client.publish(FLOW_TOPIC, payload)
        print("Sent flow:", payload)
        time.sleep(SAMPLE_INTERVAL)

if __name__ == "__main__":
    main()
