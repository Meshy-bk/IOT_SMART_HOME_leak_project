# 💧 Smart Water Leak Detection - IoT Project

This project simulates a **smart water leak detection and response system** using **Python**, **MQTT**, **SQLite**, and **PyQt5**.

The system:
- Collects sensor data (leak + flow/pressure)
- Logs readings/events to a local DB (`iot.db`)
  > Note: The included iot.db file is a sample event log database provided for project demonstration and validation.
- Detects warnings/alarms
- Automatically **closes a main water valve** and **activates a siren** on leak detection
- Provides a GUI dashboard with **Reset**, **manual valve control**, and live status

## 📦 Components (run in separate terminals)

| File | Description |
|---|---|
| `leak_manager.py` | Data manager: logs, rules, alarms, commands |
| `leak_sensor.py` | Simulates leak events (0/1) |
| `flow_sensor.py` | Simulates water flow/pressure readings |
| `valve_relay.py` | Simulates a main valve relay (OPEN/CLOSE) + publishes status |
| `siren_relay.py` | Simulates a siren (ON/OFF) + publishes status |
| `reset_button.py` | GUI button to send RESET command |
| `leak_gui.py` | PyQt5 dashboard (live readings + control) |
| `log_viewer.py` | View recent DB logs |

## ▶️ How to Run (recommended order)

1) `python leak_manager.py`  
2) `python leak_sensor.py`  
3) `python flow_sensor.py`  
4) `python valve_relay.py`  
5) `python siren_relay.py`  
6) `python reset_button.py`  
7) `python leak_gui.py`

(Optional) `python log_viewer.py`

## 🧠 MQTT Topics (overview)

**Sensors**
- `leak/sensor/leak`  → `{"leak": 0|1}`
- `leak/sensor/flow`  → `{"flow": <number>}`

**Commands**
- `leak/cmd/valve` → `OPEN | CLOSE | AUTO`
- `leak/cmd/siren` → `ON | OFF | AUTO`
- `leak/cmd/reset` → `pressed/released`

**Status**
- `leak/valve/status` → `{"mode":"AUTO|MANUAL","state":"OPEN|CLOSED"}`
- `leak/siren/status` → `{"mode":"AUTO|MANUAL","state":"ON|OFF"}`
- `leak/alarm` → string alarm/warning messages
- `leak/state` → `NORMAL | WARNING | ALARM`

## 💡 Dependencies

```bash
pip install paho-mqtt pyqt5
```
