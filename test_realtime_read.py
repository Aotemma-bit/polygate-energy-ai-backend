import asyncio
from supabase import acreate_client
from app.database.supabase_client import SUPABASE_URL, SUPABASE_KEY

async def main():
    client = await acreate_client(SUPABASE_URL, SUPABASE_KEY)

    response = (
        await client
        .table("sensor_readings")
        .select("*")
        .eq("id", 12)
        .execute()
    )

    print("ROWS:", response.data)

asyncio.run(main())
