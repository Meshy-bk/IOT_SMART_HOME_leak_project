# Smart Water Leak Detection System
# Uses public MQTT broker (HiveMQ) for demo purposes.
# Each component runs in its own terminal.

import sys, json
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout

BROKER = "broker.hivemq.com"
PORT = 1883

VALVE_CMD = "leak/cmd/valve"
VALVE_STATUS = "leak/valve/status"
SIREN_CMD = "leak/cmd/siren"
SIREN_STATUS = "leak/siren/status"
RESET_CMD = "leak/cmd/reset"

LEAK_TOPIC = "leak/sensor/leak"
FLOW_TOPIC = "leak/sensor/flow"
ALARM_TOPIC = "leak/alarm"
STATE_TOPIC = "leak/state"

class LeakGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💧 Smart Leak Detection Dashboard")
        self.resize(520, 420)
        layout = QVBoxLayout()

        self.state_lbl = QLabel("System State: --")
        self.state_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.leak_lbl = QLabel("Leak: --")
        self.flow_lbl = QLabel("Flow: --")

        self.valve_lbl = QLabel("Valve: waiting for status…")
        valve_btns = QHBoxLayout()
        btn_valve_open = QPushButton("Valve OPEN")
        btn_valve_close = QPushButton("Valve CLOSE")
        btn_valve_auto = QPushButton("Valve AUTO")
        btn_valve_open.clicked.connect(lambda: client.publish(VALVE_CMD, "OPEN"))
        btn_valve_close.clicked.connect(lambda: client.publish(VALVE_CMD, "CLOSE"))
        btn_valve_auto.clicked.connect(lambda: client.publish(VALVE_CMD, "AUTO"))
        valve_btns.addWidget(btn_valve_open)
        valve_btns.addWidget(btn_valve_close)
        valve_btns.addWidget(btn_valve_auto)

        self.siren_lbl = QLabel("Siren: waiting for status…")
        siren_btns = QHBoxLayout()
        btn_siren_on = QPushButton("Siren ON")
        btn_siren_off = QPushButton("Siren OFF")
        btn_siren_auto = QPushButton("Siren AUTO")
        btn_siren_on.clicked.connect(lambda: client.publish(SIREN_CMD, "ON"))
        btn_siren_off.clicked.connect(lambda: client.publish(SIREN_CMD, "OFF"))
        btn_siren_auto.clicked.connect(lambda: client.publish(SIREN_CMD, "AUTO"))
        siren_btns.addWidget(btn_siren_on)
        siren_btns.addWidget(btn_siren_off)
        siren_btns.addWidget(btn_siren_auto)

        reset_row = QHBoxLayout()
        btn_reset = QPushButton("RESET ALARM")
        btn_reset.setStyleSheet("font-size: 14px; padding: 8px;")
        btn_reset.clicked.connect(lambda: client.publish(RESET_CMD, "pressed"))
        reset_row.addWidget(btn_reset)

        self.alarm_lbl = QLabel("Alarms: None")
        self.alarm_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: darkred;")

        layout.addWidget(self.state_lbl)
        layout.addWidget(self.leak_lbl)
        layout.addWidget(self.flow_lbl)

        layout.addWidget(self.valve_lbl)
        layout.addLayout(valve_btns)

        layout.addWidget(self.siren_lbl)
        layout.addLayout(siren_btns)

        layout.addLayout(reset_row)
        layout.addWidget(self.alarm_lbl)

        self.setLayout(layout)

    def update_leak(self, leak_value):
        txt = "LEAK DETECTED" if int(leak_value) == 1 else "No leak"
        self.leak_lbl.setText("Leak: {}".format(txt))
        if int(leak_value) == 1:
            self.leak_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: darkred;")
        else:
            self.leak_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: green;")

    def update_flow(self, flow_value):
        self.flow_lbl.setText("Flow: {}".format(flow_value))

    def update_state(self, state):
        self.state_lbl.setText("System State: {}".format(state))
        if state == "ALARM":
            self.state_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: darkred;")
        elif state == "WARNING":
            self.state_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: orange;")
        else:
            self.state_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")

    def update_alarm(self, text):
        self.alarm_lbl.setText("ALARM: {}".format(text))

    def update_valve(self, status_json):
        try:
            status = json.loads(status_json)
            mode = status.get("mode", "AUTO")
            state = status.get("state", "OPEN")
        except:
            mode, state = "AUTO", "OPEN"
        self.valve_lbl.setText("Valve: {} ({})".format(state, mode))
        self.valve_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: {}".format("green" if state=="OPEN" else "darkred"))

    def update_siren(self, status_json):
        try:
            status = json.loads(status_json)
            mode = status.get("mode", "AUTO")
            state = status.get("state", "OFF")
        except:
            mode, state = "AUTO", "OFF"
        self.siren_lbl.setText("Siren: {} ({})".format(state, mode))
        self.siren_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: {}".format("darkred" if state=="ON" else "gray"))

def on_message(client, userdata, msg):
    data = msg.payload.decode().strip()
    if msg.topic == LEAK_TOPIC:
        try:
            gui.update_leak(json.loads(data)["leak"])
        except:
            pass
    elif msg.topic == FLOW_TOPIC:
        try:
            gui.update_flow(json.loads(data)["flow"])
        except:
            pass
    elif msg.topic == STATE_TOPIC:
        gui.update_state(data.upper())
    elif msg.topic == VALVE_STATUS:
        gui.update_valve(data)
    elif msg.topic == SIREN_STATUS:
        gui.update_siren(data)
    elif msg.topic == ALARM_TOPIC:
        gui.update_alarm(data)

client = mqtt.Client()
client.on_message = on_message

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = LeakGUI()
    gui.show()

    client.connect(BROKER, PORT, 60)
    client.subscribe("leak/#")
    client.loop_start()

    sys.exit(app.exec_())
