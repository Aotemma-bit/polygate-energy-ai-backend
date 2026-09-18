from typing import Any, Dict

from pydantic import BaseModel

from app.ml.explainability import explain_machine_prediction


class MachineExplainabilityRequest(BaseModel):
    air_temperature_K: float
    process_temperature_K: float
    rotational_speed_rpm: float
    torque_Nm: float
    tool_wear_min: float


def run_machine_explainability(
    request: MachineExplainabilityRequest,
) -> Dict[str, Any]:
    return explain_machine_prediction(
        air_temperature=request.air_temperature_K,
        process_temperature=request.process_temperature_K,
        rotational_speed=request.rotational_speed_rpm,
        torque=request.torque_Nm,
        tool_wear=request.tool_wear_min,
    )
