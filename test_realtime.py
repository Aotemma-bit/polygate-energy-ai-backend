import asyncio
from supabase import acreate_client
from app.database.supabase_client import SUPABASE_URL, SUPABASE_KEY

async def main():
    client = await acreate_client(SUPABASE_URL, SUPABASE_KEY)

    def callback(payload):
        print("REALTIME_EVENT_RECEIVED:", payload)

    def status_callback(status, error):
        print("REALTIME_STATUS:", status)
        if error:
            print("REALTIME_ERROR:", error)

    channel = client.channel("fieldflow-test")

    channel.on_postgres_changes(
        event="INSERT",
        schema="public",
        table="sensor_readings",
        callback=callback,
    )

    print("SUBSCRIBING...")
    await channel.subscribe(status_callback)

    print("SUBSCRIBED / WAITING...")
    await asyncio.sleep(300)

    print("TEST COMPLETE.")

asyncio.run(main())
