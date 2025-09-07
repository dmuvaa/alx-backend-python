#!/usr/bin/python3

"""
Objective: memory-efficient average age using a generator.
Constraints:
stream_user_ages(): yields ages one-by-one (uses yield)
Another function computes the average without SQL AVG
Print "Average age of users: <average age>"
No more than two loops total in this script
"""

from decimal import Decimal
import seed

# Optional: load .env if available so seed.connect_to_prodev() picks creds
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def stream_user_ages():
    """
    Generator that streams ages one-by-one from the database.
    Loop count note: this function contains exactly one loop.
    Yields:
        Decimal (or numeric) age values.
    """
    conn = seed.connect_to_prodev()
    cur = conn.cursor()  # unbuffered (streaming) by default in mysql-connector
    try:
        cur.execute("SELECT age FROM user_data")
        # --- Loop #1 (only loop in this function) ---
        for (age,) in cur:
            yield age
    finally:
        try:
            cur.close()
        finally:
            conn.close()


def compute_average_age():
    """
    Consumes the generator to compute the average age without SQL AVG.
    Loop count note: this function contains exactly one loop.
    Returns:
        Decimal average (two-decimal precision when printed).
    """
    total = Decimal("0")
    count = 0

    # --- Loop #2 (only loop in this function) ---
    for age in stream_user_ages():
        if age is None:
            continue
        # Ensure Decimal arithmetic
        if not isinstance(age, Decimal):
            age = Decimal(str(age))
        total += age
        count += 1

    return (total / count) if count else Decimal("0")


if __name__ == "__main__":
    avg = compute_average_age()
    # Format to two decimal places
    avg_out = avg.quantize(Decimal("0.01"))
    print(f"Average age of users: {avg_out}")
