#!/usr/bin/env python3

import os
import seed
from dotenv import load_dotenv

os.environ["MYSQL_USER"] = "dennis"

" a function that uses a generator to fetch rows one by one from the user_data table using yield"

def stream_users():
    """Yield rows from ALX_prodev.user_data one by one (single loop)."""
    conn = seed.connect_to_prodev()
    cur = conn.cursor(buffered=True)  # <-- buffered prevents 'Unread result found'
    try:
        cur.execute("SELECT user_id, name, email, age FROM user_data")
        for row in cur:               # exactly one loop
            yield row
    finally:
        cur.close()
        conn.close()