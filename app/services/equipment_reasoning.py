import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.services.equipment_intelligence import get_equipment_summary
from app.rag.search import search_documents


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_equipment_context(equipment_id: str):
    data = get_equipment_summary(equipment_id)

    equipment = data["equipment"]
    maintenance = data["maintenance"]
    sensor_readings = data["sensor_readings"]

    if not equipment:
        return None

    equipment_block = f"""
EQUIPMENT

ID: {equipment.get("equipment_id")}
Name: {equipment.get("equipment_name")}
Type: {equipment.get("equipment_type")}
Facility: {equipment.get("facility")}
Status: {equipment.get("status")}
""".strip()

    maintenance_lines = []

    for event in maintenance:
        maintenance_lines.append(
            f"""
Date: {event.get("event_date")}
Type: {event.get("event_type")}
Description: {event.get("description")}
Downtime hours: {event.get("downtime_hours")}
Cost: {event.get("cost")}
""".strip()
        )

    sensor_lines = []

    for reading in sensor_readings:
        sensor_lines.append(
            f"""
Timestamp: {reading.get("timestamp")}
Temperature: {reading.get("temperature")}
Pressure: {reading.get("pressure")}
Vibration: {reading.get("vibration")}
RPM: {reading.get("rpm")}
Flow rate: {reading.get("flow_rate")}
""".strip()
        )

    return {
        "equipment": equipment_block,
        "maintenance": "\n\n".join(maintenance_lines),
        "sensors": "\n\n".join(sensor_lines)
    }


def analyze_equipment(equipment_id: str, question: str):
    context = build_equipment_context(equipment_id)

    if not context:
        return {
            "answer": f"Equipment {equipment_id} was not found.",
            "sources": []
        }

    query_1 = (
        f"{question} compressor vibration bearing alignment lubrication "
        f"rotating equipment maintenance"
    )

    query_2 = (
        f"{question} oil gas production facility equipment inspection "
        f"maintenance safety rotating machinery"
    )

    results_1 = search_documents(
        query=query_1,
        match_threshold=0.42,
        match_count=5
    )

    results_2 = search_documents(
        query=query_2,
        match_threshold=0.42,
        match_count=5
    )

    combined = results_1 + results_2

    seen = set()
    technical_results = []

    for result in combined:
        key = (
            result["filename"],
            result["page"],
            result["content"]
        )

        if key not in seen:
            seen.add(key)
            technical_results.append(result)

    technical_results = sorted(
        technical_results,
        key=lambda x: x["similarity"],
        reverse=True
    )[:8]

    technical_context = []

    for result in technical_results:
        technical_context.append(
            f"""
Filename: {result["filename"]}
Page: {result["page"]}

{result["content"]}
""".strip()
        )

    technical_context_text = "\n\n".join(technical_context)

    system_prompt = """
You are FieldFlow, an industrial oil and gas operations intelligence assistant.

You are analyzing equipment using:
1. equipment metadata
2. maintenance history
3. sensor readings
4. retrieved technical/regulatory documents

Rules:
- Do not invent equipment thresholds.
- Do not claim a sensor value is unsafe unless a source explicitly establishes a threshold.
- You may identify trends such as increasing vibration, rising temperature, falling flow, or recurring maintenance issues.
- Clearly distinguish observed facts from inferred risk.
- Do not issue autonomous operating commands.
- Operational recommendations must be framed as items for qualified engineer review.
- Cite supporting documents using [filename, p.X].
- If technical sources do not establish a specific threshold, say so explicitly.
"""

    user_prompt = f"""
QUESTION:
{question}

EQUIPMENT DATA:
{context["equipment"]}

MAINTENANCE HISTORY:
{context["maintenance"]}

RECENT SENSOR READINGS:
{context["sensors"]}

TECHNICAL SOURCE MATERIAL:
{technical_context_text}

Provide:
1. Current condition summary
2. Evidence of deterioration or stability
3. Likely concerns
4. What is directly observed vs inferred
5. Items for qualified engineering review
"""

    response = client.responses.create(
        model="gpt-5",
        instructions=system_prompt,
        input=user_prompt
    )

    sources = []

    for result in technical_results:
        sources.append({
            "filename": result["filename"],
            "page": result["page"],
            "similarity": result["similarity"]
        })

    return {
        "answer": response.output_text,
        "sources": sources
    }