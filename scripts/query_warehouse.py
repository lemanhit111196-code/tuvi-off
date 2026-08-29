# -*- coding: utf-8 -*-
"""
query_warehouse.py
==================
Công cụ dòng lệnh để truy xuất kho 518.400 lá số Tử Vi.

Ví dụ:

  python3 scripts/query_warehouse.py                         # tổng quan
  python3 scripts/query_warehouse.py --group cuc_so          # đếm theo Cục
  python3 scripts/query_warehouse.py --group tu_vi_cung      # đếm theo vị trí Tử Vi
  python3 scripts/query_warehouse.py --group menh_cung
  python3 scripts/query_warehouse.py --group group_nam       # theo năm can-chi
  python3 scripts/query_warehouse.py --run "SELECT * FROM charts WHERE cuc_so=6 AND gender_code=1 LIMIT 5"

  # Tra toàn bộ chi tiết của một nhóm từ CSV nén (kho full-detail).
  python3 scripts/query_warehouse.py --detail-group 6 --limit 20
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "tuvi_518400.sqlite")
CSV_DIR = os.path.join(ROOT, "data", "csv_by_cuc")


def connect() -> sqlite3.Connection:
    if not os.path.exists(DB_PATH):
        sys.exit(f"Chưa có kho dữ liệu: {DB_PATH}\nChạy: python3 scripts/generate_warehouse.py")
    return sqlite3.connect(DB_PATH)


def show_overview(conn: sqlite3.Connection):
    total = conn.execute("SELECT COUNT(*) FROM charts").fetchone()[0]
    print(f"Tổng lá số trong SQLite: {total:,}")
    print("\nĐếm theo Ngũ Hành Cục (cuc_so):")
    for r in conn.execute("SELECT cuc_so, COUNT(*) FROM charts GROUP BY cuc_so ORDER BY cuc_so"):
        print(f"  Cục {r[0]} : {r[1]:,}")
    print("\nĐếm theo vị trí sao Tử Vi (tu_vi_cung):")
    for r in conn.execute("SELECT tu_vi_cung, COUNT(*) FROM charts GROUP BY tu_vi_cung ORDER BY tu_vi_cung"):
        print(f"  Cung {r[0]} : {r[1]:,}")


def run_group(conn: sqlite3.Connection, col: str, limit: int):
    cols = [r[0] for r in conn.execute('SELECT name FROM pragma_table_info("charts")').fetchall()]
    if col not in cols:
        sys.exit(f"Cột không tồn tại: {col}\nCác cột có: {', '.join(cols)}")
    rows = conn.execute(
        f'SELECT "{col}", COUNT(*) FROM charts GROUP BY "{col}" ORDER BY "{col}" LIMIT ?',
        (limit,),
    ).fetchall()
    print(f"GROUP BY {col}:")
    for k, v in rows:
        print(f"  {k:<6} {v:,}")


def run_sql(conn: sqlite3.Connection, sql: str, limit: int):
    sql = sql.strip().rstrip(";")
    if sql.lower().startswith("select"):
        sql = f"SELECT * FROM ({sql}) LIMIT {limit}"
    cur = conn.execute(sql)
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    print("\t".join(cols))
    for row in rows:
        print("\t".join(str(v) for v in row))


def detail_group(g: int, limit: int) -> None:
    path = os.path.join(CSV_DIR, f"tuvi_by_cuc_{g}.csv.gz")
    if not os.path.exists(path):
        sys.exit(f"Không có file: {path}")
    with gzip.open(path, "rt", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            print(json.dumps(row, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Truy xuất kho 518.400 lá số Tử Vi.")
    parser.add_argument("--group", metavar="COL", help="Đếm theo một cột (VD: cuc_so).")
    parser.add_argument("--run", metavar="SQL", help="Chạy câu SQL tuỳ ý.")
    parser.add_argument("--detail-group", type=int, metavar="CUC",
                        help="Đọc full-detail CSV nén của một Cục (2..6).")
    parser.add_argument("--limit", type=int, default=20, help="Giới hạn dòng hiển thị.")
    args = parser.parse_args()

    conn = connect()
    try:
        if args.detail_group:
            detail_group(args.detail_group, args.limit)
            return
        if args.group:
            run_group(conn, args.group, args.limit)
            return
        if args.run:
            run_sql(conn, args.run, args.limit)
            return
        show_overview(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
