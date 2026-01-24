# Smart Water Leak Detection System
# Uses public MQTT broker (HiveMQ) for demo purposes.
# Each component runs in its own terminal.

import sys
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import QTimer

BROKER = "broker.hivemq.com"
PORT = 1883
RESET_TOPIC = "leak/cmd/reset"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

class ResetApp(QWidget):
    def __init__(self):
        super().__init__()
        self.is_pressed = False
        self.time_left = 0

        self.setWindowTitle("💧 Leak System - Reset Button")
        self.resize(320, 200)

        layout = QVBoxLayout()
        self.label = QLabel("Reset state: released", self)
        layout.addWidget(self.label)

        self.button = QPushButton("RESET ALARM", self)
        self.button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.button.clicked.connect(self.send_reset)
        layout.addWidget(self.button)

        self.progress = QProgressBar(self)
        self.progress.setMinimum(0)
        self.progress.setMaximum(2000)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

    def send_reset(self):
        if not self.is_pressed:
            self.is_pressed = True
            self.time_left = 2000
            client.publish(RESET_TOPIC, "pressed")
            print("Reset button: pressed")
            self.label.setText("Reset state: pressed")
            self.progress.setValue(2000)
            self.timer.start(100)

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 100
            self.progress.setValue(self.time_left)
        else:
            self.timer.stop()
            self.release_button()

    def release_button(self):
        self.is_pressed = False
        client.publish(RESET_TOPIC, "released")
        print("Reset button: released")
        self.label.setText("Reset state: released")
        self.progress.setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ResetApp()
    w.show()
    sys.exit(app.exec_())
