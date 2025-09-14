import sqlite3
import functools

"""Connection decorator"""

def with_db_connection(func):
    """Open a SQLite connection to 'users.db', inject it as first arg (conn), and always close it."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

"""Cache decorator"""

query_cache = {}

def cache_query(func):
    """
    Cache results of a read-only query based on the SQL string (and optional params if you add them).
    NOTE: This simple cache never invalidates—use only when stale reads are acceptable.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = kwargs.get("query")
        if query is None and len(args) >= 1:
            # If caller passed query positionally (e.g., fetch(query)), grab it.
            query = args[0]

        if query is None:
            raise ValueError("cache_query: could not determine 'query' argument.")

        key = query  # If you later add parameters, make key = (query, tuple(params))

        if key in query_cache:
            print(f"[CACHE] hit: {key}")
            return query_cache[key]

        # Cache miss -> call the inner function (which opens the DB) and store result
        result = func(*args, **kwargs)
        query_cache[key] = result
        print(f"[CACHE] miss -> stored: {key}")
        return result
    return wrapper

# ------------------------
# Example usage
# ------------------------
@cache_query           # check cache first (no connection opened if it's a cache hit)
@with_db_connection    # open/close the connection only when needed
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

if __name__ == "__main__":
    # First call will run the query and cache the result
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print("First call:", users)

    # Second call will use the cached result (no DB connection opened)
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print("Second call:", users_again)