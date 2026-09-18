from typing import Any, Dict, List


def _pct_change(first: float, last: float) -> float:
    if first == 0:
        return 0.0

    return ((last - first) / abs(first)) * 100.0


def detect_failure_modes(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transparent engineering hypothesis engine.

    IMPORTANT:
    This does NOT confirm equipment failure.
    It identifies potential failure modes from observed sensor
    trends and maintenance-history evidence.

    Confidence is a heuristic demo classification, not a
    calibrated probability.
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
            "failure_modes": [],
            "method": (
                "Insufficient sensor data for failure-mode "
                "hypothesis generation."
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

    failure_modes = []

    # ---------------------------------------------------------
    # BEARING DEGRADATION
    # ---------------------------------------------------------

    bearing_evidence = []

    if vibration_change > 20:
        bearing_evidence.append(
            f"Vibration increased {vibration_change:.1f}%."
        )

    if "bearing" in maintenance_text:
        bearing_evidence.append(
            "Maintenance history contains bearing-related findings."
        )

    if "vibration" in maintenance_text:
        bearing_evidence.append(
            "Maintenance history contains recurring vibration findings."
        )

    if bearing_evidence:
        confidence = (
            "High"
            if len(bearing_evidence) >= 3
            else "Moderate"
        )

        failure_modes.append({
            "name": "Potential bearing degradation",
            "confidence": confidence,
            "evidence": bearing_evidence,
            "observed_signals": [
                "Rising vibration",
                "Bearing-related maintenance history",
            ],
            "engineering_note": (
                "The available evidence is consistent with a "
                "possible bearing-related condition. Physical "
                "inspection and qualified engineering assessment "
                "would be required for confirmation."
            ),
        })

    # ---------------------------------------------------------
    # MISALIGNMENT / LOOSENESS
    # ---------------------------------------------------------

    alignment_evidence = []

    if vibration_change > 20:
        alignment_evidence.append(
            f"Vibration increased {vibration_change:.1f}%."
        )

    if "alignment" in maintenance_text:
        alignment_evidence.append(
            "Maintenance history includes alignment-related work."
        )

    if "looseness" in maintenance_text:
        alignment_evidence.append(
            "Maintenance history references looseness."
        )

    if alignment_evidence:
        confidence = (
            "High"
            if len(alignment_evidence) >= 2
            else "Moderate"
        )

        failure_modes.append({
            "name": "Potential misalignment / mechanical looseness",
            "confidence": confidence,
            "evidence": alignment_evidence,
            "observed_signals": [
                "Rising vibration",
                "Alignment-related maintenance history",
            ],
            "engineering_note": (
                "The vibration trend and maintenance history may "
                "be consistent with mechanical alignment or "
                "looseness issues. Confirmation requires "
                "qualified mechanical inspection."
            ),
        })

    # ---------------------------------------------------------
    # LUBRICATION ISSUE
    # ---------------------------------------------------------

    lubrication_evidence = []

    if "lubrication" in maintenance_text:
        lubrication_evidence.append(
            "Maintenance history contains lubrication-related work."
        )

    if "lubricant" in maintenance_text:
        lubrication_evidence.append(
            "Maintenance history contains lubricant-related findings."
        )

    if "oil" in maintenance_text:
        lubrication_evidence.append(
            "Maintenance history contains oil-related maintenance."
        )

    if vibration_change > 20 and lubrication_evidence:
        lubrication_evidence.append(
            f"Vibration increased {vibration_change:.1f}%."
        )

    if lubrication_evidence:
        failure_modes.append({
            "name": "Potential lubrication-related issue",
            "confidence": (
                "Moderate"
                if len(lubrication_evidence) >= 2
                else "Low"
            ),
            "evidence": lubrication_evidence,
            "observed_signals": [
                "Lubrication/oil-related maintenance history",
                "Vibration trend"
                if vibration_change > 0
                else "No rising vibration signal",
            ],
            "engineering_note": (
                "Historical lubrication activity is an observed "
                "maintenance signal. The available data does not "
                "confirm a lubrication failure."
            ),
        })

    # ---------------------------------------------------------
    # PROCESS / PERFORMANCE DEGRADATION
    # ---------------------------------------------------------

    process_evidence = []

    if flow_change < -2:
        process_evidence.append(
            f"Flow decreased {abs(flow_change):.1f}%."
        )

    if pressure_change < -1:
        process_evidence.append(
            f"Pressure decreased {abs(pressure_change):.1f}%."
        )

    if process_evidence:
        failure_modes.append({
            "name": "Potential process / performance degradation",
            "confidence": (
                "Moderate"
                if len(process_evidence) >= 2
                else "Low"
            ),
            "evidence": process_evidence,
            "observed_signals": [
                "Declining flow",
                "Declining pressure"
                if pressure_change < 0
                else "Pressure stable",
            ],
            "engineering_note": (
                "The observed process-variable changes may indicate "
                "a change in equipment or process performance. "
                "Additional operating context is required."
            ),
        })

    # ---------------------------------------------------------
    # TEMPERATURE SIGNAL
    # ---------------------------------------------------------

    if temperature_change > 5 and vibration_change > 20:
        failure_modes.append({
            "name": "Potential rotating-equipment thermal/mechanical issue",
            "confidence": "Moderate",
            "evidence": [
                f"Temperature increased {temperature_change:.1f}%.",
                f"Vibration increased {vibration_change:.1f}%.",
            ],
            "observed_signals": [
                "Rising temperature",
                "Rising vibration",
            ],
            "engineering_note": (
                "The combination of rising temperature and "
                "vibration is an observed condition pattern. "
                "The underlying cause cannot be confirmed from "
                "the available data alone."
            ),
        })

    return {
        "equipment_id": equipment.get("equipment_id"),
        "equipment_name": equipment.get("equipment_name"),
        "status": (
            "Potential failure modes identified"
            if failure_modes
            else "No strong failure-mode signals identified"
        ),
        "failure_modes": failure_modes,
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
            "Transparent rule-based engineering hypothesis "
            "generation using observed sensor trends and "
            "maintenance-history evidence. Confidence is a "
            "heuristic classification, not a calibrated probability. "
            "Potential failure modes are not confirmed failures."
        ),
    }