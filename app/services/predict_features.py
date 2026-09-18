from statistics import mean, pstdev
from typing import Any, Dict, List


def _safe_pct_change(first: float, last: float) -> float:
    if first == 0:
        return 0.0

    return ((last - first) / abs(first)) * 100.0


def _mean(values: List[float]) -> float:
    return mean(values) if values else 0.0


def _std(values: List[float]) -> float:
    return pstdev(values) if len(values) > 1 else 0.0


def _trend(values: List[float]) -> float:
    """
    Simple first-to-last trend.

    Positive = increasing.
    Negative = decreasing.
    """

    if len(values) < 2:
        return 0.0

    return values[-1] - values[0]


def build_predictive_features(
    sensor_readings: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Convert raw sensor readings into ML-ready time-series features.

    This module performs feature engineering only.
    It does not predict equipment failure.
    """

    if not sensor_readings:
        return {
            "sample_count": 0,
            "features": {},
            "status": "Insufficient sensor data",
            "method": (
                "No sensor readings were available for feature extraction."
            ),
        }

    readings = sorted(
        sensor_readings,
        key=lambda x: x.get("timestamp", ""),
    )

    vibration = [
        float(r["vibration"])
        for r in readings
        if r.get("vibration") is not None
    ]

    temperature = [
        float(r["temperature"])
        for r in readings
        if r.get("temperature") is not None
    ]

    flow = [
        float(r["flow_rate"])
        for r in readings
        if r.get("flow_rate") is not None
    ]

    pressure = [
        float(r["pressure"])
        for r in readings
        if r.get("pressure") is not None
    ]

    features = {
        # Dataset size
        "sample_count": len(readings),

        # -------------------------
        # Vibration
        # -------------------------
        "vibration_mean": round(_mean(vibration), 4),
        "vibration_std": round(_std(vibration), 4),
        "vibration_min": round(min(vibration), 4) if vibration else 0.0,
        "vibration_max": round(max(vibration), 4) if vibration else 0.0,
        "vibration_trend": round(_trend(vibration), 4),
        "vibration_change_percent": round(
            _safe_pct_change(vibration[0], vibration[-1]),
            2,
        )
        if vibration
        else 0.0,

        # -------------------------
        # Temperature
        # -------------------------
        "temperature_mean": round(_mean(temperature), 4),
        "temperature_std": round(_std(temperature), 4),
        "temperature_min": (
            round(min(temperature), 4)
            if temperature
            else 0.0
        ),
        "temperature_max": (
            round(max(temperature), 4)
            if temperature
            else 0.0
        ),
        "temperature_trend": round(_trend(temperature), 4),
        "temperature_change_percent": round(
            _safe_pct_change(temperature[0], temperature[-1]),
            2,
        )
        if temperature
        else 0.0,

        # -------------------------
        # Flow
        # -------------------------
        "flow_mean": round(_mean(flow), 4),
        "flow_std": round(_std(flow), 4),
        "flow_min": round(min(flow), 4) if flow else 0.0,
        "flow_max": round(max(flow), 4) if flow else 0.0,
        "flow_trend": round(_trend(flow), 4),
        "flow_change_percent": round(
            _safe_pct_change(flow[0], flow[-1]),
            2,
        )
        if flow
        else 0.0,

        # -------------------------
        # Pressure
        # -------------------------
        "pressure_mean": round(_mean(pressure), 4),
        "pressure_std": round(_std(pressure), 4),
        "pressure_min": (
            round(min(pressure), 4)
            if pressure
            else 0.0
        ),
        "pressure_max": (
            round(max(pressure), 4)
            if pressure
            else 0.0
        ),
        "pressure_trend": round(_trend(pressure), 4),
        "pressure_change_percent": round(
            _safe_pct_change(pressure[0], pressure[-1]),
            2,
        )
        if pressure
        else 0.0,
    }

    return {
        "sample_count": len(readings),
        "features": features,
        "status": "Feature extraction complete",
        "method": (
            "Time-series feature engineering using descriptive statistics "
            "and first-to-last sensor trends. No failure prediction is "
            "performed by this module."
        ),
    }