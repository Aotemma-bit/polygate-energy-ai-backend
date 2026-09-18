import time
import random
import requests
from datetime import datetime, timezone

URL = "http://127.0.0.1:8000/equipment/C-104/sensor"

temperature = 107.0
pressure = 63.5
vibration = 15.8
rpm = 3750.0
flow_rate = 105.5

print("C-104 LIVE SENSOR SIMULATOR")
print("Sending telemetry every 10 seconds...")
print("Press CTRL+C to stop.")

while True:
    temperature += random.uniform(-0.4, 0.7)
    pressure += random.uniform(-0.3, 0.2)
    vibration += random.uniform(-0.15, 0.25)
    rpm += random.uniform(-8, 10)
    flow_rate += random.uniform(-0.5, 0.3)

    payload = {
        "equipment_id": "C-104",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": round(temperature, 2),
        "pressure": round(pressure, 2),
        "vibration": round(vibration, 2),
        "rpm": round(rpm, 0),
        "flow_rate": round(flow_rate, 2),
    }

    try:
        response = requests.post(URL, json=payload, timeout=10)
        response.raise_for_status()
        print(
            f"{payload['timestamp']} | "
            f"T={payload['temperature']} | "
            f"P={payload['pressure']} | "
            f"V={payload['vibration']} | "
            f"RPM={payload['rpm']} | "
            f"Flow={payload['flow_rate']}"
        )
    except Exception as e:
        print("ERROR:", e)

    time.sleep(10)
