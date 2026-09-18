from typing import Any, Dict, List


def _pct_change(first: float, last: float) -> float:
    if first == 0:
        return 0.0

    return ((last - first) / abs(first)) * 100.0


def generate_maintenance_recommendations(
    summary: Dict[str, Any],
    failure_mode_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Transparent maintenance recommendation engine.

    This is decision-support logic for the Polygate Energy AI
    demonstration.

    Recommendations are generated from observed sensor trends
    and maintenance-history evidence.

    They are NOT autonomous maintenance commands and do not
    replace qualified engineering procedures, OEM instructions,
    inspection plans, or safety processes.
    """

    readings: List[Dict[str, Any]] = summary.get(
        "sensor_readings",
        []
    )

    maintenance: List[Dict[str, Any]] = summary.get(
        "maintenance",
        []
    )

    equipment = summary.get("equipment") or {}

    if not readings:
        return {
            "equipment_id": equipment.get("equipment_id"),
            "equipment_name": equipment.get("equipment_name"),
            "status": "Insufficient Data",
            "recommendations": [],
            "method": (
                "Insufficient sensor data for maintenance "
                "recommendation generation."
            ),
        }

    readings = sorted(
        readings,
        key=lambda x: str(x.get("timestamp", ""))
    )

    earliest = readings[0]
    latest = readings[-1]

    vibration_change = _pct_change(
        float(earliest.get("vibration", 0)),
        float(latest.get("vibration", 0)),
    )

    temperature_change = _pct_change(
        float(earliest.get("temperature", 0)),
        float(latest.get("temperature", 0)),
    )

    flow_change = _pct_change(
        float(earliest.get("flow_rate", 0)),
        float(latest.get("flow_rate", 0)),
    )

    pressure_change = _pct_change(
        float(earliest.get("pressure", 0)),
        float(latest.get("pressure", 0)),
    )

    maintenance_text = " ".join(
        str(event.get("description", "")).lower()
        for event in maintenance
    )

    recommendations = []

    # ---------------------------------------------------------
    # 1. BEARING INSPECTION
    # ---------------------------------------------------------

    bearing_history = (
        "bearing" in maintenance_text
        or "vibration" in maintenance_text
    )

    if vibration_change > 20 and bearing_history:
        recommendations.append({
            "priority": 1,
            "action": "Review drive-end bearing condition",
            "category": "Mechanical Inspection",
            "trigger": [
                f"Vibration increased {vibration_change:.1f}%.",
                "Maintenance history contains bearing/vibration findings.",
            ],
            "recommended_review": [
                "Review recent bearing inspection records.",
                "Assess current drive-end bearing condition.",
                "Compare current vibration behavior with approved "
                "equipment monitoring practices.",
            ],
            "reason": (
                "The available sensor trend and maintenance history "
                "provide a basis for reviewing the bearing condition."
            ),
            "requires_engineer_review": True,
        })

    # ---------------------------------------------------------
    # 2. ALIGNMENT / MECHANICAL CONDITION
    # ---------------------------------------------------------

    alignment_history = (
        "alignment" in maintenance_text
        or "looseness" in maintenance_text
    )

    if vibration_change > 20 and alignment_history:
        recommendations.append({
            "priority": 2,
            "action": "Review shaft alignment and mechanical condition",
            "category": "Mechanical Inspection",
            "trigger": [
                f"Vibration increased {vibration_change:.1f}%.",
                "Maintenance history contains alignment-related work.",
            ],
            "recommended_review": [
                "Review the most recent alignment inspection.",
                "Assess whether alignment verification is warranted.",
                "Check applicable mechanical inspection procedures.",
            ],
            "reason": (
                "The rising vibration trend combined with previous "
                "alignment-related maintenance supports a mechanical "
                "condition review."
            ),
            "requires_engineer_review": True,
        })

    # ---------------------------------------------------------
    # 3. LUBRICATION REVIEW
    # ---------------------------------------------------------

    lubrication_history = (
        "lubrication" in maintenance_text
        or "lubricant" in maintenance_text
        or "oil" in maintenance_text
    )

    if vibration_change > 20 and lubrication_history:
        recommendations.append({
            "priority": 3,
            "action": "Review lubrication and oil-maintenance status",
            "category": "Lubrication Review",
            "trigger": [
                f"Vibration increased {vibration_change:.1f}%.",
                "Maintenance history contains lubrication/oil work.",
            ],
            "recommended_review": [
                "Review the most recent lubrication activity.",
                "Verify maintenance records and applicable lubricant "
                "requirements.",
                "Assess whether additional inspection is appropriate.",
            ],
            "reason": (
                "The combination of rising vibration and historical "
                "lubrication-related maintenance supports reviewing "
                "lubrication status."
            ),
            "requires_engineer_review": True,
        })

    # ---------------------------------------------------------
    # 4. PROCESS PERFORMANCE REVIEW
    # ---------------------------------------------------------

    process_trigger = (
        flow_change < -2
        or pressure_change < -1
    )

    if process_trigger:
        triggers = []

        if flow_change < -2:
            triggers.append(
                f"Flow decreased {abs(flow_change):.1f}%."
            )

        if pressure_change < -1:
            triggers.append(
                f"Pressure decreased {abs(pressure_change):.1f}%."
            )

        recommendations.append({
            "priority": 4,
            "action": "Review compressor process performance",
            "category": "Performance Review",
            "trigger": triggers,
            "recommended_review": [
                "Review recent operating conditions.",
                "Check whether the flow and pressure changes "
                "correspond to an intentional process change.",
                "Compare current performance with approved operating "
                "and engineering references.",
            ],
            "reason": (
                "Observed changes in flow and/or pressure justify "
                "reviewing current process and equipment performance."
            ),
            "requires_engineer_review": True,
        })

    # ---------------------------------------------------------
    # 5. TEMPERATURE + VIBRATION REVIEW
    # ---------------------------------------------------------

    if temperature_change > 5 and vibration_change > 20:
        recommendations.append({
            "priority": 5,
            "action": "Review combined thermal and vibration trend",
            "category": "Condition Monitoring",
            "trigger": [
                f"Temperature increased {temperature_change:.1f}%.",
                f"Vibration increased {vibration_change:.1f}%.",
            ],
            "recommended_review": [
                "Review the recent temperature and vibration trend.",
                "Check for changes in operating conditions.",
                "Determine whether additional condition monitoring "
                "or inspection is warranted.",
            ],
            "reason": (
                "The simultaneous increase in temperature and vibration "
                "is an observed condition pattern that warrants review."
            ),
            "requires_engineer_review": True,
        })

    # ---------------------------------------------------------
    # SORT BY PRIORITY
    # ---------------------------------------------------------

    recommendations.sort(
        key=lambda item: item["priority"]
    )

    return {
        "equipment_id": equipment.get("equipment_id"),
        "equipment_name": equipment.get("equipment_name"),
        "status": (
            "Maintenance recommendations generated"
            if recommendations
            else "No recommendation triggers identified"
        ),
        "recommendations": recommendations,
        "observations": {
            "vibration_change_percent": round(
                vibration_change,
                1
            ),
            "temperature_change_percent": round(
                temperature_change,
                1
            ),
            "flow_change_percent": round(
                flow_change,
                1
            ),
            "pressure_change_percent": round(
                pressure_change,
                1
            ),
        },
        "method": (
            "Transparent rule-based maintenance decision support "
            "using observed sensor trends and maintenance-history "
            "signals. Recommendations require qualified engineering "
            "review and do not constitute autonomous maintenance commands."
        ),
    }