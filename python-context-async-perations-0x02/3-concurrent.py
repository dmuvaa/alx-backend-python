import asyncio
import aiosqlite

DB_PATH = "async_example.db"

# --- Setup: create table + seed sample rows if empty (async, one-time) ---
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id   INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age  INTEGER NOT NULL
            )
        """)
        # Check if we have data already
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            (count,) = await cur.fetchone()

        if count == 0:
            await db.executemany(
                "INSERT INTO users(name, age) VALUES (?, ?)",
                [
                    ("Ada Lovelace", 36),
                    ("Linus Torvalds", 55),
                    ("Grace Hopper", 85),
                    ("Guido van Rossum", 68),
                    ("Alice", 22),
                ],
            )
            await db.commit()

# --- Required functions ---
async def async_fetch_users():
    """Fetch all users (returns list of aiosqlite.Row)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users") as cur:
            return await cur.fetchall()

async def async_fetch_older_users():
    """Fetch users older than 40 (returns list of aiosqlite.Row)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cur:
            return await cur.fetchall()

# --- Run both concurrently with asyncio.gather ---
async def fetch_concurrently():
    await init_db()  # Make sure DB exists and has data

    all_task = async_fetch_users()
    older_task = async_fetch_older_users()

    all_users, older_users = await asyncio.gather(all_task, older_task)

    print("\nAll users:")
    for row in all_users:
        print(dict(row))

    print("\nUsers older than 40:")
    for row in older_users:
        print(dict(row))

# --- Entry point ---
if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
