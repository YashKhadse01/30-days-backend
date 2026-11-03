import asyncio
from sqlalchemy import text
from app.database import engine

async def main():
    try:
        async with engine.connect() as connection:
            result = await connection.execute(
                text("SELECT current_database()")
            )
            print("Connected database:", result.scalar_one())
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())