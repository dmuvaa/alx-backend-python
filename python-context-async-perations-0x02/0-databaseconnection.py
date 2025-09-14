import sqlite3

class DatabaseConnection:
    """Context manager for safe SQLite connections."""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None

    def __enter__(self) -> sqlite3.Connection:
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        finally:
            self.conn.close()
        return False

# --- demo (creates a table once, then runs the required SELECT) ---
if __name__ == "__main__":
    """setup: create table & sample data (safe to run multiple times)"""
    with DatabaseConnection("example.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT
            )
        """)
        # Insert a couple rows if table is empty
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO users(name, email) VALUES(?, ?)",
                [("Ada Lovelace", "ada@example.com"),
                 ("Linus Torvalds", "linus@example.com")]
            )

    with DatabaseConnection("example.db") as conn:
        rows = conn.execute("SELECT * FROM users").fetchall()
        for row in rows:
            print(dict(row))
