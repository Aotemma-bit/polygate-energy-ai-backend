from app.database.supabase_client import supabase


def get_equipment_summary(equipment_id: str):
    equipment_response = (
        supabase
        .table("equipment")
        .select("*")
        .eq("equipment_id", equipment_id)
        .limit(1)
        .execute()
    )

    maintenance_response = (
        supabase
        .table("maintenance_events")
        .select("*")
        .eq("equipment_id", equipment_id)
        .order("event_date", desc=True)
        .limit(10)
        .execute()
    )

    sensor_response = (
        supabase
        .table("sensor_readings")
        .select("*")
        .eq("equipment_id", equipment_id)
        .order("timestamp", desc=True)
        .limit(10)
        .execute()
    )

    equipment = (
        equipment_response.data[0]
        if equipment_response.data
        else None
    )

    return {
        "equipment": equipment,
        "maintenance": maintenance_response.data,
        "sensor_readings": sensor_response.data
    }