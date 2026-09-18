from typing import Any, Dict, List

from app.services.predict_features import build_predictive_features


def _pct_change(first: float, last: float) -> float:
    if first == 0:
        return 0.0

    return ((last - first) / abs(first)) * 100.0


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def generate_prediction_view(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Polygate Predict — transparent prediction-readiness/trend engine.

    This version intentionally does NOT produce a calibrated failure
    probability or remaining-useful-life estimate.

    It converts available recent sensor history into observable trend
    signals and ML-ready engineered features for the predictive-
    maintenance UI.
    """

    readings: List[Dict[str, Any]] = summary.get("sensor_readings", [])
    maintenance: List[Dict[str, Any]] = summary.get("maintenance", [])

    if not readings:
        return {
            "status": "Insufficient data",
            "prediction_mode": "Trend analysis only",
            "confidence": "Insufficient data",
            "prediction_horizon": "Unavailable",
            "anomaly_index": 0.0,
            "signals": [],
            "timeline": [],
            "predictive_features": {
                "sample_count": 0,
                "features": {},
                "status": "Insufficient sensor data",
            },
            "method": (
                "Trend analysis requires sensor history. "
                "No calibrated failure probability or remaining "
                "useful life is produced."
            ),
        }

    readings = sorted(
        readings,
        key=lambda x: str(x.get("timestamp", "")),
    )

    # ---------------------------------------------------------
    # ML feature engineering
    # ---------------------------------------------------------

    predictive_features = build_predictive_features(readings)

    # ---------------------------------------------------------
    # Current transparent trend calculations
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Transparent heuristic anomaly index
    # ---------------------------------------------------------

    positive_signals = [
        max(0.0, vibration_change),
        max(0.0, temperature_change),
        max(0.0, -flow_change),
        max(0.0, -pressure_change),
    ]

    anomaly_index = round(
        _clamp(
            (
                min(100.0, positive_signals[0] * 0.8)
                + min(40.0, positive_signals[1] * 1.5)
                + min(25.0, positive_signals[2] * 4.0)
                + min(15.0, positive_signals[3] * 4.0)
            ),
            0.0,
            100.0,
        ),
        1,
    )

    # ---------------------------------------------------------
    # Predictive signals
    # ---------------------------------------------------------

    signals = []

    if vibration_change > 0:
        signals.append(
            {
                "name": "Vibration",
                "change_percent": round(vibration_change, 1),
                "direction": "Rising",
                "severity": (
                    "High"
                    if vibration_change >= 25
                    else "Moderate"
                ),
                "interpretation": (
                    "Strongest observed trend signal in the "
                    "available window."
                ),
            }
        )

    if temperature_change > 0:
        signals.append(
            {
                "name": "Temperature",
                "change_percent": round(temperature_change, 1),
                "direction": "Rising",
                "severity": "Moderate",
                "interpretation": (
                    "Temperature is increasing across the "
                    "available readings."
                ),
            }
        )

    if flow_change < 0:
        signals.append(
            {
                "name": "Flow",
                "change_percent": round(flow_change, 1),
                "direction": "Declining",
                "severity": "Moderate",
                "interpretation": (
                    "Flow is declining across the available readings."
                ),
            }
        )

    if pressure_change < 0:
        signals.append(
            {
                "name": "Pressure",
                "change_percent": round(pressure_change, 1),
                "direction": "Declining",
                "severity": "Low",
                "interpretation": (
                    "Pressure is slightly lower at the latest reading."
                ),
            }
        )

    # ---------------------------------------------------------
    # Maintenance history signal
    # ---------------------------------------------------------

    recurring = []

    for event in maintenance:
        description = str(
            event.get("description", "")
        ).lower()

        if any(
            keyword in description
            for keyword in (
                "vibration",
                "bearing",
                "alignment",
                "lubrication",
                "oil",
            )
        ):
            recurring.append(event)

    if recurring:
        signals.append(
            {
                "name": "Maintenance History",
                "change_percent": None,
                "direction": "Recurring findings",
                "severity": "High",
                "interpretation": (
                    f"{len(recurring)} relevant historical "
                    "maintenance events are available."
                ),
            }
        )

    # ---------------------------------------------------------
    # Engineering action plan
    # ---------------------------------------------------------

    action_plan = []

    if vibration_change > 0:
        action_plan.append({
            "priority": "High" if vibration_change >= 25 else "Medium",
            "trigger": "Vibration rising",
            "recommended_review": "Review drive-end bearing and mechanical condition",
            "evidence": f"Vibration changed {vibration_change:.1f}% across the available sensor window."
        })

    if temperature_change > 0:
        action_plan.append({
            "priority": "Medium",
            "trigger": "Temperature rising",
            "recommended_review": "Review thermal condition and cooling performance",
            "evidence": f"Temperature changed {temperature_change:.1f}% across the available sensor window."
        })

    if flow_change < 0:
        action_plan.append({
            "priority": "Medium",
            "trigger": "Flow declining",
            "recommended_review": "Review flow path, process conditions, and operating state",
            "evidence": f"Flow changed {flow_change:.1f}% across the available sensor window."
        })

    if pressure_change < 0:
        action_plan.append({
            "priority": "Low",
            "trigger": "Pressure declining",
            "recommended_review": "Review pressure conditions and process stability",
            "evidence": f"Pressure changed {pressure_change:.1f}% across the available sensor window."
        })

    if recurring:
        action_plan.append({
            "priority": "High",
            "trigger": "Recurring maintenance findings",
            "recommended_review": "Review recurring bearing, vibration, alignment, lubrication, or oil findings",
            "evidence": f"{len(recurring)} relevant historical maintenance events are available."
        })

    if not action_plan:
        action_plan.append({
            "priority": "Routine",
            "trigger": "No material directional signal",
            "recommended_review": "Continue routine monitoring",
            "evidence": "No rising or declining sensor trend met the current action thresholds."
        })

    # ---------------------------------------------------------
    # Overall trend state
    # ---------------------------------------------------------

    if anomaly_index >= 70:
        status = "Strong trend signal"
        confidence = "Heuristic — high signal strength"
    elif anomaly_index >= 40:
        status = "Emerging trend signal"
        confidence = "Heuristic — moderate signal strength"
    else:
        status = "Low trend signal"
        confidence = "Heuristic — low signal strength"

    # ---------------------------------------------------------
    # Timeline for visualization
    # ---------------------------------------------------------

    timeline = [
        {
            "timestamp": str(
                reading.get("timestamp", "")
            ),
            "vibration": reading.get("vibration"),
            "temperature": reading.get("temperature"),
            "flow_rate": reading.get("flow_rate"),
            "pressure": reading.get("pressure"),
        }
        for reading in readings
    ]

    # ---------------------------------------------------------
    # Final response
    # ---------------------------------------------------------

    return {
        "status": status,
        "prediction_mode": "Trend analysis only",
        "confidence": confidence,
        "prediction_horizon": "Current trend window",
        "anomaly_index": anomaly_index,
        "signals": signals,
        "action_plan": action_plan,
        "timeline": timeline,
        "observations": {
            "vibration_change_percent": round(
                vibration_change,
                1,
            ),
            "temperature_change_percent": round(
                temperature_change,
                1,
            ),
            "flow_change_percent": round(
                flow_change,
                1,
            ),
            "pressure_change_percent": round(
                pressure_change,
                1,
            ),
        },
        "predictive_features": predictive_features,
        "method": (
            "Transparent trend-based predictive-maintenance "
            "prototype using recent sensor changes, maintenance "
            "history, and engineered time-series features. "
            "It does not produce a calibrated failure probability, "
            "failure date, or remaining useful life. Those require "
            "validated training data and evaluation."
        ),
    }
