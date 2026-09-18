import asyncio
import inspect

from supabase import acreate_client
from app.database.supabase_client import SUPABASE_URL, SUPABASE_KEY


async def main():
    client = await acreate_client(SUPABASE_URL, SUPABASE_KEY)

    channel = client.channel("test-channel")

    print("CHANNEL_TYPE:", type(channel).__name__)
    print("HAS_ON_POSTGRES_CHANGES:", hasattr(channel, "on_postgres_changes"))
    print("HAS_SUBSCRIBE:", hasattr(channel, "subscribe"))

    if hasattr(channel, "subscribe"):
        print("SUBSCRIBE_SIGNATURE:", inspect.signature(channel.subscribe))

    await client.close()


asyncio.run(main())
