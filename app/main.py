import json
import os

from pydantic import BaseModel

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.database.supabase_client import supabase

from app.rag.search import search_documents
from app.rag.answer import answer_question, stream_answer_question

from app.services.equipment_intelligence import get_equipment_summary
from app.services.equipment_reasoning import analyze_equipment
from app.services.predict_engine import generate_prediction_view
from app.services.risk_engine import calculate_equipment_risk
from app.services.failure_mode_engine import detect_failure_modes
from app.services.maintenance_recommendation_engine import (
    generate_maintenance_recommendations
)
from app.services.operations_dashboard import get_operations_overview

from app.ml.api import (
    MachinePredictionRequest,
    run_machine_prediction,
)
from app.ml.model_info import get_model_info
from app.ml.validation_info import get_validation_info



app = FastAPI(
    title="Polygate Energy AI",
    version="1.0.0",
    description="Industrial intelligence platform for energy operations",
)


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in FRONTEND_URL.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EquipmentAnalysisRequest(BaseModel):
    equipment_id: str
    question: str


class FieldFlowSearchRequest(BaseModel):
    query: str
    match_threshold: float = 0.40
    match_count: int = 5


class FieldFlowAskRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "message": "Polygate Energy AI API"
    }


@app.get("/health")
def health():
    return {
        "status": "ready",
        "platform": "Polygate Energy AI"
    }


@app.get("/equipment")
def get_equipment():
    try:
        response = (
            supabase
            .table("equipment")
            .select("*")
            .execute()
        )

        return {
            "count": len(response.data),
            "equipment": response.data
        }

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }


@app.post("/equipment/demo")
def create_demo_equipment():
    try:
        payload = {
            "equipment_id": "C-104",
            "equipment_name": "Main Gas Compressor",
            "equipment_type": "Compressor",
            "facility": "Field Alpha",
            "manufacturer": "Synthetic Demo Manufacturer",
            "status": "Operational"
        }

        response = (
            supabase
            .table("equipment")
            .upsert(
                payload,
                on_conflict="equipment_id"
            )
            .execute()
        )

        return response.data

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }


@app.get("/equipment/{equipment_id}/intelligence")
def equipment_intelligence(equipment_id: str):
    try:
        result = get_equipment_summary(equipment_id)

        if not result["equipment"]:
            return {
                "error": f"Equipment {equipment_id} not found"
            }

        return result

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }


@app.get("/equipment/{equipment_id}/risk")
def get_equipment_risk(equipment_id: str):
    try:
        summary = get_equipment_summary(equipment_id)

        if not summary["equipment"]:
            return {
                "equipment_id": equipment_id,
                "error": f"Equipment {equipment_id} not found"
            }

        risk = calculate_equipment_risk(summary)

        return {
            "equipment_id": equipment_id,
            "equipment_name": summary["equipment"].get(
                "equipment_name"
            ),
            **risk,
        }

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }


@app.get("/equipment/{equipment_id}/failure-modes")
def get_equipment_failure_modes(equipment_id: str):
    try:
        summary = get_equipment_summary(equipment_id)

        if not summary["equipment"]:
            return {
                "equipment_id": equipment_id,
                "error": f"Equipment {equipment_id} not found"
            }

        result = detect_failure_modes(summary)

        return result

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }


@app.post("/equipment/analyze")
def equipment_analysis(request: EquipmentAnalysisRequest):
    try:
        result = analyze_equipment(
            equipment_id=request.equipment_id,
            question=request.question
        )

        return {
            "equipment_id": request.equipment_id,
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }


@app.post("/predict/ml")
def predict_ml(request: MachinePredictionRequest):
    try:
        return run_machine_prediction(request)

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }


@app.get("/predict/ml/info")
def predict_ml_info():
    try:
        return get_model_info()

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }


@app.get("/predict/ml/validation")
def predict_ml_validation():
    try:
        return get_validation_info()

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }


@app.get("/equipment/{equipment_id}/predict")
def equipment_predict(equipment_id: str):
    try:
        summary = get_equipment_summary(equipment_id)

        if not summary["equipment"]:
            return {
                "equipment_id": equipment_id,
                "error": f"Equipment {equipment_id} not found"
            }

        result = generate_prediction_view(summary)

        return {
            "equipment_id": equipment_id,
            "equipment_name": summary["equipment"].get(
                "equipment_name"
            ),
            **result,
        }

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }


@app.post("/fieldflow/search")
def fieldflow_search(request: FieldFlowSearchRequest):
    try:
        results = search_documents(
            query=request.query,
            match_threshold=request.match_threshold,
            match_count=request.match_count
        )

        return {
            "query": request.query,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }


@app.post("/fieldflow/ask")
def fieldflow_ask(request: FieldFlowAskRequest):
    try:
        result = answer_question(request.question)

        return {
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }


@app.get("/equipment/{equipment_id}/maintenance-recommendations")
def get_maintenance_recommendations(equipment_id: str):
    try:
        summary = get_equipment_summary(equipment_id)

        if not summary["equipment"]:
            return {
                "equipment_id": equipment_id,
                "error": f"Equipment {equipment_id} not found"
            }

        failure_mode_result = detect_failure_modes(summary)

        result = generate_maintenance_recommendations(
            summary=summary,
            failure_mode_result=failure_mode_result
        )

        return result

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }


@app.get("/operations/overview")
def operations_overview():
    try:
        return get_operations_overview()

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }



from app.ml.explainability_api import (
    MachineExplainabilityRequest,
    run_machine_explainability,
)

@app.post("/predict/ml/explain")
def explain_machine(request: MachineExplainabilityRequest):
    return run_machine_explainability(request)

from app.services.event_engine import generate_equipment_events

@app.get("/equipment/{equipment_id}/events")
def equipment_events(equipment_id: str):
    return generate_equipment_events(equipment_id)



class SensorReadingRequest(BaseModel):
    equipment_id: str
    timestamp: str
    temperature: float
    pressure: float
    vibration: float
    rpm: float
    flow_rate: float


@app.post("/equipment/{equipment_id}/sensor")
def ingest_sensor_reading(
    equipment_id: str,
    request: SensorReadingRequest,
):
    try:
        if request.equipment_id != equipment_id:
            return {
                "error": "equipment_id in path does not match request body."
            }

        payload = {
            "equipment_id": equipment_id,
            "timestamp": request.timestamp,
            "temperature": request.temperature,
            "pressure": request.pressure,
            "vibration": request.vibration,
            "rpm": request.rpm,
            "flow_rate": request.flow_rate,
        }

        response = (
            supabase
            .table("sensor_readings")
            .insert(payload)
            .execute()
        )

        summary = get_equipment_summary(equipment_id)
        events = generate_equipment_events(equipment_id)
        risk = calculate_equipment_risk(summary)

        return {
            "status": "Sensor reading ingested and asset state refreshed",
            "equipment_id": equipment_id,
            "reading": response.data,
            "asset_state": {
                "latest_sensor": (
                    summary["sensor_readings"][0]
                    if summary["sensor_readings"]
                    else None
                ),
                "risk": risk,
                "events": events,
            },
            "method": (
                "Sensor reading persisted to the sensor history, "
                "then current event and risk analytics were recalculated. "
                "Analytics are decision support for qualified engineering "
                "review and are not autonomous safety alarms or confirmed failures."
            ),
        }

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__,
        }

@app.post("/fieldflow/ask/stream")
def fieldflow_ask_stream(request: FieldFlowAskRequest):
    def generate():
        try:
            for event in stream_answer_question(request.question):
                if event["type"] == "token":
                    yield f"data: {event['text']}\n\n"

                elif event["type"] == "sources":
                    yield f"event: sources\ndata: {json.dumps(event['sources'])}\n\n"

                elif event["type"] == "error":
                    yield f"event: error\ndata: {event['message']}\n\n"

        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

