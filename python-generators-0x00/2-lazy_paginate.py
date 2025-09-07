#!/usr/bin/python3
# 2-lazy_paginate.py

seed = __import__('seed')


def paginate_users(page_size, offset):
    """Fetch one page of users using LIMIT/OFFSET and return a list of dict rows."""
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(f"SELECT * FROM user_data ORDER BY user_id LIMIT {int(page_size)} OFFSET {int(offset)}")
        rows = cursor.fetchall()
        return rows
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        connection.close()


def lazy_paginate(page_size):
    """
    Lazily yield pages of users.
    Only ONE loop is used in this entire module (the while loop below).
    """
    if page_size is None or int(page_size) <= 0:
        raise ValueError("page_size must be a positive integer")

    offset = 0
    # === Only loop ===
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            return
        yield page
        offset += len(page)


# Alias to satisfy 3-main.py usage:
lazy_pagination = lazy_paginate
