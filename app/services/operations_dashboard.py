from typing import Any, Dict, List

from app.database.supabase_client import supabase
from app.services.equipment_intelligence import get_equipment_summary
from app.services.risk_engine import calculate_equipment_risk
from app.services.failure_mode_engine import detect_failure_modes


def get_operations_overview() -> Dict[str, Any]:
    """
    Operations Command Center aggregation.

    Uses equipment, sensor, maintenance, risk and failure-mode
    data already available inside Polygate Energy AI.

    This endpoint is read-only decision support.
    """

    equipment_response = (
        supabase
        .table("equipment")
        .select("*")
        .execute()
    )

    equipment_rows: List[Dict[str, Any]] = (
        equipment_response.data or []
    )

    assets = []
    maintenance_event_count = 0

    for equipment in equipment_rows:
        equipment_id = equipment.get("equipment_id")

        if not equipment_id:
            continue

        summary = get_equipment_summary(equipment_id)

        if not summary.get("equipment"):
            continue

        risk = calculate_equipment_risk(summary)
        failure_modes = detect_failure_modes(summary)

        maintenance_events = summary.get(
            "maintenance",
            []
        )

        maintenance_event_count += len(
            maintenance_events
        )

        top_failure_mode = None

        if failure_modes.get("failure_modes"):
            top_failure_mode = (
                failure_modes["failure_modes"][0]
            )

        assets.append({
            "equipment_id": equipment_id,
            "equipment_name": equipment.get(
                "equipment_name"
            ),
            "equipment_type": equipment.get(
                "equipment_type"
            ),
            "facility": equipment.get(
                "facility"
            ),
            "status": equipment.get(
                "status"
            ),
            "risk_score": risk.get(
                "score",
                0
            ),
            "risk_level": risk.get(
                "level",
                "Unknown"
            ),
            "risk_label": risk.get(
                "label",
                "Unknown"
            ),
            "maintenance_events": len(
                maintenance_events
            ),
            "top_failure_mode": (
                top_failure_mode.get("name")
                if top_failure_mode
                else None
            ),
            "top_failure_confidence": (
                top_failure_mode.get("confidence")
                if top_failure_mode
                else None
            ),
        })

    assets.sort(
        key=lambda x: x.get(
            "risk_score",
            0
        ),
        reverse=True
    )

    total_assets = len(assets)

    critical_assets = [
        asset
        for asset in assets
        if asset["risk_level"] == "Critical"
    ]

    elevated_assets = [
        asset
        for asset in assets
        if asset["risk_level"] == "Elevated"
    ]

    watch_assets = [
        asset
        for asset in assets
        if asset["risk_level"] == "Watch"
    ]

    normal_assets = [
        asset
        for asset in assets
        if asset["risk_level"] == "Normal"
    ]

    engineering_concerns: Dict[str, int] = {}

    for asset in assets:
        concern = asset.get(
            "top_failure_mode"
        )

        if concern:
            engineering_concerns[concern] = (
                engineering_concerns.get(
                    concern,
                    0
                ) + 1
            )

    ranked_concerns = sorted(
        engineering_concerns.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return {
        "status": "Operational overview generated",

        "summary": {
            "total_assets": total_assets,
            "critical_assets": len(
                critical_assets
            ),
            "elevated_assets": len(
                elevated_assets
            ),
            "watch_assets": len(
                watch_assets
            ),
            "normal_assets": len(
                normal_assets
            ),
            "maintenance_events": maintenance_event_count,
        },

        "assets": assets,

        "engineering_concerns": [
            {
                "name": name,
                "asset_count": count,
            }
            for name, count in ranked_concerns
        ],

        "method": (
            "Read-only operations aggregation using equipment "
            "records, recent sensor trends, maintenance history, "
            "the transparent quantitative risk engine and "
            "failure-mode hypothesis engine."
        ),
    }