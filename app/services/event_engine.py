from typing import Any, Dict

from app.services.equipment_intelligence import get_equipment_summary


def generate_equipment_events(equipment_id: str) -> Dict[str, Any]:
    intelligence = get_equipment_summary(equipment_id)

    if intelligence.get("error"):
        return intelligence

    readings = intelligence.get("sensor_readings") or []

    if not readings:
        return {
            "equipment_id": equipment_id,
            "status": "No sensor data available",
            "sensor_window": {
                "sample_count": 0,
                "oldest_timestamp": None,
                "newest_timestamp": None,
            },
            "events": [],
            "observed_changes": {
                "vibration_percent": 0.0,
                "temperature_percent": 0.0,
                "flow_percent": 0.0,
                "pressure_percent": 0.0,
            },
            "method": "No events generated because no sensor readings were available.",
        }

    newest = readings[0]
    oldest = readings[-1]

    def pct_change(new: float, old: float) -> float:
        if old == 0:
            return 0.0
        return ((new - old) / abs(old)) * 100.0

    vibration_change = pct_change(
        float(newest["vibration"]),
        float(oldest["vibration"]),
    )

    temperature_change = pct_change(
        float(newest["temperature"]),
        float(oldest["temperature"]),
    )

    flow_change = pct_change(
        float(newest["flow_rate"]),
        float(oldest["flow_rate"]),
    )

    pressure_change = pct_change(
        float(newest["pressure"]),
        float(oldest["pressure"]),
    )

    events = []

    if vibration_change >= 50:
        events.append(
            {
                "event_type": "Condition Signal",
                "severity": "High",
                "status": "Open",
                "signal": "Vibration",
                "equipment_id": equipment_id,
                "timestamp": newest["timestamp"],
                "message": f"Vibration increased {vibration_change:.1f}% across the available sensor window.",
                "recommended_review": "Review current mechanical condition, bearing condition, alignment and approved vibration-monitoring practices.",
            }
        )
    elif vibration_change >= 20:
        events.append(
            {
                "event_type": "Condition Signal",
                "severity": "Medium",
                "status": "Open",
                "signal": "Vibration",
                "equipment_id": equipment_id,
                "timestamp": newest["timestamp"],
                "message": f"Vibration increased {vibration_change:.1f}% across the available sensor window.",
                "recommended_review": "Review the current vibration trend against approved equipment monitoring practices.",
            }
        )

    if temperature_change >= 10:
        events.append(
            {
                "event_type": "Condition Signal",
                "severity": "Medium",
                "status": "Open",
                "signal": "Temperature",
                "equipment_id": equipment_id,
                "timestamp": newest["timestamp"],
                "message": f"Temperature increased {temperature_change:.1f}% across the available sensor window.",
                "recommended_review": "Review the thermal trend together with operating conditions and approved equipment limits.",
            }
        )

    if flow_change <= -2:
        events.append(
            {
                "event_type": "Performance Signal",
                "severity": "Medium",
                "status": "Open",
                "signal": "Flow Rate",
                "equipment_id": equipment_id,
                "timestamp": newest["timestamp"],
                "message": f"Flow rate decreased {abs(flow_change):.1f}% across the available sensor window.",
                "recommended_review": "Review compressor process performance and operating conditions.",
            }
        )

    if pressure_change <= -1:
        events.append(
            {
                "event_type": "Performance Signal",
                "severity": "Low",
                "status": "Open",
                "signal": "Pressure",
                "equipment_id": equipment_id,
                "timestamp": newest["timestamp"],
                "message": f"Pressure decreased {abs(pressure_change):.1f}% across the available sensor window.",
                "recommended_review": "Review the pressure trend alongside process conditions and approved operating practices.",
            }
        )

    return {
        "equipment_id": equipment_id,
        "status": "Events generated",
        "sensor_window": {
            "sample_count": len(readings),
            "oldest_timestamp": oldest["timestamp"],
            "newest_timestamp": newest["timestamp"],
        },
        "events": events,
        "observed_changes": {
            "vibration_percent": round(vibration_change, 2),
            "temperature_percent": round(temperature_change, 2),
            "flow_percent": round(flow_change, 2),
            "pressure_percent": round(pressure_change, 2),
        },
        "method": "Transparent rule-based event detection using observed sensor trends. Events are analytical signals for qualified engineering review, not autonomous safety alarms or confirmed equipment failures.",
    }
