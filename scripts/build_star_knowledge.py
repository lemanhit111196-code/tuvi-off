# -*- coding: utf-8 -*-
"""
build_star_knowledge.py
=======================
Sinh "kho kiến thức Sao ở Cung" từ `star_knowledge_data.py` và ghi vào ba đầu ra:

  - data/star_knowledge/star_cung_knowledge.json   (đơn giản, dễ load)
  - data/star_knowledge/star_cung_knowledge.csv.gz (bảng truy vấn bằng CSV)
  - data/tuvi_518400.sqlite  ->  bảng `star_cung_knowledge` (join charts)

Nội dung mỗi dòng:
  (star_key, star_name, star_group, nature, cung_index, cung_name,
   description, keywords)

`cung_index` là vị trí TƯƠNG ĐỐI so với cung Mệnh (0..11). Muốn lấy cho 1 lá số
bất kỳ: cung = (pos_star - menh_cung) % 12.

Chạy:
    python3 scripts/build_star_knowledge.py
"""

from __future__ import annotations

import csv
import gzip
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.star_knowledge_data import (  # noqa: E402
    CUNG_ESSENCE,
    CUNG_NAMES,
    DETAIL_EXTRA,
    DETAIL_MAIN,
    STAR_META,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
KNOW_DIR = os.path.join(DATA_DIR, "star_knowledge")
DB_PATH = os.path.join(DATA_DIR, "tuvi_518400.sqlite")
CSV_PATH = os.path.join(KNOW_DIR, "star_cung_knowledge.csv.gz")
JSON_PATH = os.path.join(KNOW_DIR, "star_cung_knowledge.json")


def gen_rows():
    rows = []
    for star_key, meta in STAR_META.items():
        # Toàn bộ từ khoá mặc định.
        keywords = [meta["name"], meta["group"], meta["nature"]]
        for cung_index in range(12):
            cung_name, cung_text = CUNG_ESSENCE[cung_index]
            if star_key in DETAIL_MAIN and cung_index in DETAIL_MAIN[star_key]:
                desc = DETAIL_MAIN[star_key][cung_index]
            elif star_key in DETAIL_EXTRA and cung_index in DETAIL_EXTRA[star_key]:
                desc = DETAIL_EXTRA[star_key][cung_index]
            else:
                desc = (
                    f"{meta['name']} ở cung {cung_name}: {meta['general']} "
                    f"Cung {cung_name} liên quan {cung_text.rstrip('.').lower()}. "
                    f"Xét tốt/xấu cần nhìn tổng thể cách cục và các sao hội chiếu."
                )
            rows.append({
                "star_key": star_key,
                "star_name": meta["name"],
                "star_group": meta["group"],
                "nature": meta["nature"],
                "cung_index": cung_index,
                "cung_name": cung_name,
                "description": desc,
                "keywords": ", ".join(keywords),
            })
    return rows


def write_csv(rows):
    os.makedirs(KNOW_DIR, exist_ok=True)
    with gzip.open(CSV_PATH, "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_json(rows):
    os.makedirs(KNOW_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


def write_sqlite(rows):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS star_cung_knowledge (
            id INTEGER PRIMARY KEY,
            star_key TEXT NOT NULL,
            star_name TEXT NOT NULL,
            star_group TEXT NOT NULL,
            nature TEXT NOT NULL,
            cung_index INTEGER NOT NULL,
            cung_name TEXT NOT NULL,
            description TEXT NOT NULL,
            keywords TEXT NOT NULL
        )
    """)
    cur.execute("DELETE FROM star_cung_knowledge")
    cur.executemany(
        "INSERT INTO star_cung_knowledge "
        "(star_key, star_name, star_group, nature, cung_index, cung_name, description, keywords) "
        "VALUES (?,?,?,?,?,?,?,?)",
        [(r["star_key"], r["star_name"], r["star_group"], r["nature"],
          r["cung_index"], r["cung_name"], r["description"], r["keywords"]) for r in rows],
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sk_star ON star_cung_knowledge(star_key)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sk_cung ON star_cung_knowledge(cung_index)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sk_key_cung ON star_cung_knowledge(star_key, cung_index)")
    conn.commit()
    conn.close()


def main():
    rows = gen_rows()
    write_csv(rows)
    write_json(rows)
    write_sqlite(rows)
    print(f"Đã tạo {len(rows):,} dòng kiến thức.")
    print(f"  CSV   : {CSV_PATH}")
    print(f"  JSON  : {JSON_PATH}")
    print(f"  SQLite:{DB_PATH} (bảng star_cung_knowledge)")


if __name__ == "__main__":
    main()
