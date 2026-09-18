from typing import Any, Dict, List


def _pct_change(first: float, last: float) -> float:
    if first == 0:
        return 0.0
    return ((last - first) / abs(first)) * 100.0


def calculate_equipment_risk(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transparent Polygate demo risk model.

    This is an analytics score for portfolio/demo purposes.
    It is NOT an OEM alarm limit, safety limit, or failure prediction.
    """

    readings: List[Dict[str, Any]] = summary.get("sensor_readings", [])
    maintenance: List[Dict[str, Any]] = summary.get("maintenance", [])

    if not readings:
        return {
            "score": 0,
            "level": "Unknown",
            "label": "Insufficient Data",
            "components": [],
            "signals": [],
            "method": "Insufficient sensor data for demo risk scoring.",
        }

    readings = sorted(
        readings,
        key=lambda x: str(x.get("timestamp", ""))
    )

    first = readings[0]
    latest = readings[-1]

    vibration_change = _pct_change(
        float(first.get("vibration", 0)),
        float(latest.get("vibration", 0)),
    )

    temperature_change = _pct_change(
        float(first.get("temperature", 0)),
        float(latest.get("temperature", 0)),
    )

    flow_change = _pct_change(
        float(first.get("flow_rate", 0)),
        float(latest.get("flow_rate", 0)),
    )

    pressure_change = _pct_change(
        float(first.get("pressure", 0)),
        float(latest.get("pressure", 0)),
    )

    flow_decline = max(0.0, -flow_change)
    pressure_decline = max(0.0, -pressure_change)

    vibration_points = min(
        30.0,
        max(0.0, vibration_change) * 0.40,
    )

    temperature_points = min(
        15.0,
        max(0.0, temperature_change) * 1.00,
    )

    flow_points = min(
        10.0,
        flow_decline * 2.00,
    )

    pressure_points = min(
        5.0,
        pressure_decline * 2.00,
    )

    relevant_maintenance = []

    keywords = (
        "vibration",
        "bearing",
        "alignment",
        "lubrication",
        "lubricant",
    )

    for event in maintenance:
        description = str(
            event.get("description", "")
        ).lower()

        if any(keyword in description for keyword in keywords):
            relevant_maintenance.append(event)

    maintenance_points = min(
        25.0,
        len(relevant_maintenance) * 6.0,
    )

    recent_monitoring_points = 0.0

    for event in maintenance:
        event_type = str(
            event.get("event_type", "")
        ).lower()

        if event_type == "condition monitoring":
            recent_monitoring_points = 8.0
            break

    total_score = round(
        min(
            100.0,
            vibration_points
            + temperature_points
            + flow_points
            + pressure_points
            + maintenance_points
            + recent_monitoring_points,
        ),
        1,
    )

    if total_score >= 80:
        level = "Critical"
    elif total_score >= 60:
        level = "Elevated"
    elif total_score >= 35:
        level = "Watch"
    else:
        level = "Normal"

    signals = []

    if vibration_change > 0:
        signals.append({
            "name": "Vibration",
            "status": "High" if vibration_change >= 25 else "Moderate",
            "change_percent": round(vibration_change, 1),
            "direction": "rising",
        })

    if temperature_change > 0:
        signals.append({
            "name": "Temperature",
            "status": "Moderate",
            "change_percent": round(temperature_change, 1),
            "direction": "rising",
        })

    if flow_decline > 0:
        signals.append({
            "name": "Flow",
            "status": "Moderate",
            "change_percent": round(flow_decline, 1),
            "direction": "declining",
        })

    if relevant_maintenance:
        signals.append({
            "name": "Maintenance History",
            "status": "High",
            "events": len(relevant_maintenance),
            "direction": "recurring findings",
        })

    components = [
        {
            "name": "Vibration trend",
            "points": round(vibration_points, 1),
            "max_points": 30,
        },
        {
            "name": "Temperature trend",
            "points": round(temperature_points, 1),
            "max_points": 15,
        },
        {
            "name": "Flow deterioration",
            "points": round(flow_points, 1),
            "max_points": 10,
        },
        {
            "name": "Pressure trend",
            "points": round(pressure_points, 1),
            "max_points": 5,
        },
        {
            "name": "Maintenance history",
            "points": round(maintenance_points, 1),
            "max_points": 25,
        },
        {
            "name": "Recent condition monitoring",
            "points": round(recent_monitoring_points, 1),
            "max_points": 8,
        },
    ]

    return {
        "score": total_score,
        "level": level,
        "label": f"{level} Risk",
        "signals": signals,
        "components": components,
        "observations": {
            "vibration_change_percent": round(vibration_change, 1),
            "temperature_change_percent": round(temperature_change, 1),
            "flow_change_percent": round(flow_change, 1),
            "pressure_change_percent": round(pressure_change, 1),
        },
        "method": (
            "Transparent rule-based demo analytics using recent "
            "sensor trends and maintenance-history signals. "
            "Not an OEM limit, safety threshold, or failure prediction."
        ),
    }