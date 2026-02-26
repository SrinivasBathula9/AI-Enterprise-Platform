import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from qdrant_client import QdrantClient
import redis
from app.config import get_settings

async def test_postgres(url):
    print(f"Testing Postgres at {url}...")
    try:
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        print("✅ Postgres connection successful!")
    except Exception as e:
        print(f"❌ Postgres connection failed: {e}")

def test_redis(url):
    print(f"Testing Redis at {url}...")
    try:
        r = redis.from_url(url)
        r.ping()
        print("✅ Redis connection successful!")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")

def test_qdrant(url):
    print(f"Testing Qdrant at {url}...")
    try:
        client = QdrantClient(url=url)
        client.get_collections()
        print("✅ Qdrant connection successful!")
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")

async def main():
    settings = get_settings()
    await test_postgres(settings.database_url)
    test_redis(settings.redis_url)
    test_qdrant(settings.qdrant_url)

if __name__ == "__main__":
    asyncio.run(main())
