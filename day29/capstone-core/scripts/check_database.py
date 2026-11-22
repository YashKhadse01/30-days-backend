import asyncio

from sqlalchemy import text

from capstone_core.db.session import engine


async def main() -> None:
    try:
        async with engine.connect() as connection:
            result = await connection.execute(
                text("SELECT current_database(), current_user")
            )
            database, user = result.one()

            print(f"Connected to database: {database}")
            print(f"Database user: {user}")
            print("Async SQLAlchemy connection successful.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
