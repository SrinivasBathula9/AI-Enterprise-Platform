import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.assistant import Assistant
from app.models.workspace import Workspace

async def check_db():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Assistant))
        assistants = res.scalars().all()
        print(f"Total assistants in DB: {len(assistants)}")
        for a in assistants:
            print(f"- {a.name} (ID: {a.id}, is_default: {a.is_default})")
        
        res = await db.execute(select(Workspace))
        workspaces = res.scalars().all()
        print(f"\nTotal workspaces in DB: {len(workspaces)}")
        for w in workspaces:
            print(f"- {w.name} (Owner: {w.owner_id})")

if __name__ == "__main__":
    asyncio.run(check_db())
