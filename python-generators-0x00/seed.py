#!/usr/bin/env python3

"""
seed.py — Set up ALX_prodev.user_data and seed it from user_data.csv

Prototypes implemented:
- def connect_db()
- def create_database(connection)
- def connect_to_prodev()
- def create_table(connection)
- def insert_data(connection, data)

Usage:
    python3 seed.py --csv user_data.csv
Environment (optional):
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD
Defaults:
    host=127.0.0.1, port=3306, user=root, password=prompted if missing
"""

import os
import csv
import uuid
import getpass
import argparse
from decimal import Decimal, InvalidOperation

from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode

load_dotenv()

# --- constants (can be overridden by env) ---
DB_NAME = os.getenv("DB_NAME", "ALX_prodev")
TABLE_NAME = os.getenv("TABLE_NAME", "user_data")

def connect_db():
    """connects to the mysql database server (no DB selected)"""
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD") or getpass.getpass(f"Password for MySQL user '{user}': ")
    try:
        return mysql.connector.connect(host=host, port=port, user=user, password=password, autocommit=True)
    except mysql.connector.Error as err:
        raise SystemExit(f"[connect_db] {err}")

def create_database(connection):
    """creates the database ALX_prodev if it does not exist"""
    try:
        with connection.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
            )
    except mysql.connector.Error as err:
        raise SystemExit(f"[create_database] {err}")

def connect_to_prodev():
    """connects the the ALX_prodev database in MYSQL"""
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD") or getpass.getpass(f"Password for MySQL user '{user}': ")
    try:
        return mysql.connector.connect(host=host, port=port, user=user, password=password, database=DB_NAME)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            raise SystemExit(f"[connect_to_prodev] DB '{DB_NAME}' not found; run create_database() first.")
        raise SystemExit(f"[connect_to_prodev] {err}")

def create_table(connection):
    """creates a table user_data if it does not exists with the required fields"""
    ddl = f"""
    CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` (
        `user_id` CHAR(36) NOT NULL,
        `name`    VARCHAR(255) NOT NULL,
        `email`   VARCHAR(255) NOT NULL,
        `age`     DECIMAL(5,2) NOT NULL,
        PRIMARY KEY (`user_id`),
        UNIQUE KEY `uniq_email` (`email`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """
    try:
        with connection.cursor() as cur:
            cur.execute(ddl)
        connection.commit()
    except mysql.connector.Error as err:
        raise SystemExit(f"[create_table] {err}")

def _normalize_row(row):
    lower = {k.strip().lower(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
    name = lower.get("name")
    email = lower.get("email")
    uid = lower.get("user_id") or lower.get("userid") or lower.get("id")

    if not name or not email:
        raise ValueError("missing name/email")

    if not uid:
        uid = str(uuid.uuid4())
    else:
        uid = str(uid)[:36]

    try:
        age_val = Decimal(str(lower.get("age"))).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        raise ValueError(f"invalid age: {row.get('age')}")
    return (uid, name, email, age_val)

def insert_data(connection, data):
    """
    inserts data in the database if it does not exist
    Accepts either:
      - iterable of tuples (user_id, name, email, age), or
      - a CSV path (str), which will be loaded via load_csv()
    """
    if isinstance(data, str):
        data = load_csv(data)

    if not isinstance(data, (list, tuple)):
        raise SystemExit("[insert_data] Parameters for query must be list or tuple (or CSV filepath string).")

    sql = f"INSERT IGNORE INTO `{TABLE_NAME}` (user_id, name, email, age) VALUES (%s, %s, %s, %s)"
    try:
        with connection.cursor() as cur:
            cur.executemany(sql, data)
        connection.commit()
    except mysql.connector.Error as err:
        raise SystemExit(f"[insert_data] {err}")

def load_csv(csv_path):
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit("CSV has no header row.")
        for i, row in enumerate(reader, start=2):
            try:
                rows.append(_normalize_row(row))
            except ValueError as e:
                print(f"[load_csv] Skipping row {i}: {e}")
    return rows

def main():
    parser = argparse.ArgumentParser(description="Seed ALX_prodev.user_data from CSV.")
    parser.add_argument("--csv", default="user_data.csv", help="Path to CSV file")
    args = parser.parse_args()

    # 1) connect to server, create DB
    server_conn = connect_db()
    create_database(server_conn)
    server_conn.close()

    # 2) connect to DB
    db_conn = connect_to_prodev()

    # 3) create table
    create_table(db_conn)

    # 4) load + insert
    data = load_csv(args.csv)
    if not data:
        print("[main] No valid rows to insert.")
        db_conn.close()
        return
    insert_data(db_conn, data)
    print(f"[main] Insert attempted for {len(data)} rows (duplicates ignored).")

    with db_conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM `{TABLE_NAME}`;")
        total = cur.fetchone()[0]
    print(f"[main] Current total rows in {DB_NAME}.{TABLE_NAME}: {total}")
    db_conn.close()

if __name__ == "__main__":
    main()
