import sqlite3
import json

DB_FILE = "iot.db"

def show_logs(filter_topic=None, limit=20):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    if filter_topic:
        cur.execute("SELECT timestamp, sensor, value FROM logs WHERE sensor=? ORDER BY timestamp DESC LIMIT ?",
                    (filter_topic, limit))
    else:
        cur.execute("SELECT timestamp, sensor, value FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))

    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("No logs found.")
        return

    for ts, topic, val in rows:
        try:
            val_json = json.loads(val)
            print(f"[{ts}] {topic} → {json.dumps(val_json, indent=2)}")
        except:
            print(f"[{ts}] {topic} → {val}")

if __name__ == "__main__":
    print("💧 Smart Leak Log Viewer")
    print("Options:")
    print("  1) Show last 20 logs (all)")
    print("  2) Show only leak sensor logs")
    print("  3) Show only flow sensor logs")
    print("  4) Show only valve status logs")
    print("  5) Show only siren status logs")
    print("  6) Show only alarms")
    print()

    choice = input("Select option: ").strip()

    if choice == "1":
        show_logs()
    elif choice == "2":
        show_logs("leak/sensor/leak")
    elif choice == "3":
        show_logs("leak/sensor/flow")
    elif choice == "4":
        show_logs("leak/valve/status")
    elif choice == "5":
        show_logs("leak/siren/status")
    elif choice == "6":
        show_logs("leak/alarm")
    else:
        print("Invalid option.")
