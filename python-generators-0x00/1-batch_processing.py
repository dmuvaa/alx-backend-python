#!/usr/bin/env python3
# 2-stream_users_batches.py

"""
Prototypes:
    def stream_users_in_batches(batch_size)
    def batch_processing(batch_size)

Behavior:
- stream_users_in_batches(batch_size): yields lists of rows (user_id, name, email, age)
  fetched from MySQL in batches, using keyset pagination (ORDER BY user_id).
- batch_processing(batch_size): yields lists filtered to users with age > 25.

Assumptions:
- You have seed.py with connect_to_prodev() available in the same directory.
- Table: ALX_prodev.user_data(user_id CHAR(36) PK, name, email, age DECIMAL(5,2)).

Notes:
- No more than 3 loops are used in this file:
    * ONE while-loop in stream_users_in_batches
    * ONE for-loop in batch_processing
    * (Filtering uses a list comprehension.)
"""

import os
from decimal import Decimal
from dotenv import load_dotenv
import seed

# Load .env (if present) and default the MySQL user to 'dennis' unless overridden.
load_dotenv()
os.environ.setdefault("MYSQL_USER", "dennis")


def stream_users_in_batches(batch_size):
    """
    Yields batches (list[tuple]) of (user_id, name, email, age).

    Uses keyset pagination on user_id to avoid unread-result issues and
    to ensure each batch is a separate DB query.

    Args:
        batch_size (int): max number of rows per batch.

    Yields:
        list[tuple]: [(user_id, name, email, age), ...] with length <= batch_size
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")

    conn = seed.connect_to_prodev()
    last_id = None  # keyset bookmark (lexicographic on CHAR(36) UUID)
    try:
        # Exactly ONE loop in this function
        while True:
            cur = conn.cursor()
            try:
                if last_id is None:
                    cur.execute(
                        "SELECT user_id, name, email, age "
                        "FROM user_data "
                        "ORDER BY user_id "
                        "LIMIT %s",
                        (batch_size,),
                    )
                else:
                    cur.execute(
                        "SELECT user_id, name, email, age "
                        "FROM user_data "
                        "WHERE user_id > %s "
                        "ORDER BY user_id "
                        "LIMIT %s",
                        (last_id, batch_size),
                    )

                batch = cur.fetchall()  # fully read this batch, safe to close cursor
                if not batch:
                    return  # end of stream

                yield batch
                last_id = batch[-1][0]  # advance bookmark
            finally:
                cur.close()
    finally:
        conn.close()


def batch_processing(batch_size):
    """
    Processes each batch to filter users over age 25, yielding filtered batches.

    Args:
        batch_size (int): batch size for fetching.

    Yields:
        list[tuple]: filtered rows where age > 25
    """
    threshold = Decimal("25")
    # Exactly ONE loop in this function
    for batch in stream_users_in_batches(batch_size):
        filtered = [row for row in batch if row[3] is not None and row[3] > threshold]
        if filtered:
            yield filtered
