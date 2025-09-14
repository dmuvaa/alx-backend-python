import sqlite3
import functools

#### decorator to log SQL queries
def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Try to get the SQL string from kwargs (query=...) or the first positional arg"""
        query = kwargs.get("query")
        if query is None and len(args) >= 1:
            query = args[0]
        print(f"[SQL] {query}")            # log before executing
        return func(*args, **kwargs)       # run the original function and return its result
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")