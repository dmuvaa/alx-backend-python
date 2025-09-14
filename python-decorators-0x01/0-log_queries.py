import sqlite3
import functools
from datetime import datetime

"""decorator to log SQL queries (with timestamp)"""
def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Extract the SQL query from kwargs (query=...) or the first positional arg"""
        query = kwargs.get("query")
        if query is None and len(args) >= 1:
            query = args[0]

        # Timestamp the log using datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [SQL] {query}")

        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query (with timestamp)
users = fetch_all_users(query="SELECT * FROM users")