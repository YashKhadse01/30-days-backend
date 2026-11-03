import asyncio
from app.database import engine
from app.models import Base

async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    print("Database tables created successfully!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())