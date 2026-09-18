from typing import Any, Dict

from pydantic import BaseModel

from app.ml.model_service import predict_machine_failure


class MachinePredictionRequest(BaseModel):
    air_temperature_K: float
    process_temperature_K: float
    rotational_speed_rpm: float
    torque_Nm: float
    tool_wear_min: float


def run_machine_prediction(
    request: MachinePredictionRequest,
) -> Dict[str, Any]:
    return predict_machine_failure(
        air_temperature=request.air_temperature_K,
        process_temperature=request.process_temperature_K,
        rotational_speed=request.rotational_speed_rpm,
        torque=request.torque_Nm,
        tool_wear=request.tool_wear_min,
    )