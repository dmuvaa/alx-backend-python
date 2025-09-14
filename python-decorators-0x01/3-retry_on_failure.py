import time
import sqlite3
import functools

#### paste your with_db_decorator here
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

#### retry decorator
def retry_on_failure(retries=3, delay=2):
    """
    Retry the wrapped function up to `retries` times if it raises a transient
    sqlite error. Wait `delay` seconds between attempts.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
                    last_exc = e
                    if attempt == retries:
                        # no more attempts left, re-raise
                        raise
                    print(f"[RETRY] attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
            # Should never reach here; re-raise just in case
            raise last_exc
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure
users = fetch_users_with_retry()
print(users)