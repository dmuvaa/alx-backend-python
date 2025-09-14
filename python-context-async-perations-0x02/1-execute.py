import sqlite3
from typing import Optional, Sequence, Any

class ExecuteQuery:
    """Context manager that opens a connection, executes a query, returns the result, and cleans up."""
    def __init__(self, db_path: str, query: str, params: Optional[Sequence[Any]] = None):
        self.db_path = db_path
        self.query = query
        self.params = params or []
        self.conn: Optional[sqlite3.Connection] = None
        self.cur: Optional[sqlite3.Cursor] = None
        self._result = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cur = self.conn.cursor()
        self.cur.execute(self.query, self.params)

        # Return rows for SELECT, or write-op info for others
        if self.query.strip().lower().startswith("select"):
            self._result = self.cur.fetchall()
        else:
            self._result = {"rowcount": self.cur.rowcount, "lastrowid": self.cur.lastrowid}
        return self._result

    def __exit__(self, exc_type, exc, tb):
        try:
            if self.conn is not None:
                if exc_type is None:
                    self.conn.commit()
                else:
                    self.conn.rollback()
        finally:
            if self.cur is not None:
                self.cur.close()
            if self.conn is not None:
                self.conn.close()
        return False  # do not suppress exceptions

"""Demo setup (optional).
Create a small table and a few rows so the SELECT will return data."""
with ExecuteQuery("example.db", """
CREATE TABLE IF NOT EXISTS users(
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age  INTEGER NOT NULL
)
"""):
    pass

# Insert seed data only if empty
with ExecuteQuery("example.db", "SELECT COUNT(*) AS c FROM users") as rows:
    if rows[0]["c"] == 0:
        with ExecuteQuery(
            "example.db",
            "INSERT INTO users(name, age) VALUES (?, ?), (?, ?), (?, ?)",
            ("Ada Lovelace", 36, "Linus Torvalds", 55, "Alice", 22)
        ):
            pass

with ExecuteQuery("example.db", "SELECT * FROM users WHERE age > ?", (25,)) as result_rows:
    for row in result_rows:
        print(dict(row))
