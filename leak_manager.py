# Smart Water Leak Detection System
# Uses public MQTT broker (HiveMQ) for demo purposes.
# Each component runs in its own terminal.

import paho.mqtt.client as mqtt
import sqlite3, json, time

BROKER = "broker.hivemq.com"
PORT = 1883

# DB Setup
conn = sqlite3.connect("iot.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS logs (
    timestamp TEXT,
    sensor TEXT,
    value TEXT
)""")
conn.commit()

def log_data(topic, value):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO logs VALUES (?, ?, ?)", (ts, topic, value))
    conn.commit()
    print(f"{ts} | {topic}: {value}")

# Topics
LEAK_TOPIC = "leak/sensor/leak"
FLOW_TOPIC = "leak/sensor/flow"

VALVE_CMD = "leak/cmd/valve"
VALVE_STATUS = "leak/valve/status"

SIREN_CMD = "leak/cmd/siren"
SIREN_STATUS = "leak/siren/status"

RESET_TOPIC = "leak/cmd/reset"

ALARM_TOPIC = "leak/alarm"
STATE_TOPIC = "leak/state"

# Thresholds
FLOW_WARNING_THRESHOLD = 35
FLOW_ALARM_THRESHOLD = 60  # optional extra alarm condition

alarm_active = False
last_leak = 0

def publish_state(client, state):
    client.publish(STATE_TOPIC, state, retain=True)
    log_data(STATE_TOPIC, state)

def raise_alarm(client, msg):
    client.publish(ALARM_TOPIC, msg)
    log_data(ALARM_TOPIC, msg)

def close_water(client, reason):
    client.publish(VALVE_CMD, "CLOSE")
    client.publish(SIREN_CMD, "ON")
    raise_alarm(client, reason)
    publish_state(client, "ALARM")

def clear_alarm(client):
    # For safety: stop siren; keep valve CLOSED until manual OPEN
    client.publish(SIREN_CMD, "OFF")
    raise_alarm(client, "✅ Alarm reset. (Valve remains CLOSED until manual OPEN)")
    publish_state(client, "NORMAL")

def on_message(client, userdata, msg):
    global alarm_active, last_leak
    data = msg.payload.decode().strip()

    # Relay statuses (JSON)
    if msg.topic in [VALVE_STATUS, SIREN_STATUS]:
        try:
            status = json.loads(data)
            log_data(msg.topic, json.dumps(status))
        except Exception as e:
            print(f"Error parsing status on {msg.topic}: {e}")
        return

    # Reset
    if msg.topic == RESET_TOPIC:
        log_data(RESET_TOPIC, data)
        if data.lower() == "pressed":
            alarm_active = False
            clear_alarm(client)
        return

    # Leak sensor
    if msg.topic == LEAK_TOPIC:
        try:
            log_data(LEAK_TOPIC, data)
            leak_val = int(json.loads(data).get("leak", 0))
            last_leak = leak_val

            if leak_val == 1 and not alarm_active:
                alarm_active = True
                close_water(client, "🚨 LEAK DETECTED! Water closed + siren ON")
            elif leak_val == 0 and not alarm_active:
                publish_state(client, "NORMAL")

        except Exception as e:
            print("Error parsing leak:", e)
        return

    # Flow sensor
    if msg.topic == FLOW_TOPIC:
        try:
            log_data(FLOW_TOPIC, data)
            flow = float(json.loads(data).get("flow", 0))

            if (not alarm_active) and last_leak == 0 and flow >= FLOW_WARNING_THRESHOLD:
                publish_state(client, "WARNING")
                raise_alarm(client, f"⚠️ High flow detected ({flow}). Possible issue (no leak flag yet).")

            if (not alarm_active) and flow >= FLOW_ALARM_THRESHOLD:
                alarm_active = True
                close_water(client, f"🚨 Abnormal flow alarm ({flow}). Water closed + siren ON")

        except Exception as e:
            print("Error parsing flow:", e)
        return

    # If someone publishes alarms externally
    if msg.topic == ALARM_TOPIC:
        log_data(ALARM_TOPIC, data)

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe("leak/#")

print("💧 Leak Manager running... logging sensors + relay status + alarms")
publish_state(client, "NORMAL")
client.loop_forever()
