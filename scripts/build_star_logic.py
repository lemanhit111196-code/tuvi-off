# -*- coding: utf-8 -*-
"""
build_star_logic.py
===================
Sinh kho LOGIC LUẬN GIẢI SAO:
  - `star_logic`            : 1 dòng/sao (109 hoặc một bộ sao logic) — bản chất, tích cực,
                              tiêu cực, thẻ ngữ nghĩa, thiên tính.
  - `star_interaction_logic`: mọi cặp tương tác giữa các sao trong `LOGIC_STARS`
                              (chính tinh + phụ tinh + tứ hoá + cố định + tuần không).

Đầu ra:
  - data/luan_giai/star_logic.json
  - data/luan_giai/star_interaction_logic.json
  - bảng `star_logic`, `star_interaction_logic` trong SQLite.

Chạy:
  python3 scripts/build_star_logic.py
"""

from __future__ import annotations

import itertools
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.star_logic_engine import (  # noqa: E402
    LOGIC_STARS,
    classify_interaction,
    pair_logic,
    star_logic,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
LUAN_DIR = os.path.join(DATA_DIR, "luan_giai")
DB_PATH = os.path.join(DATA_DIR, "tuvi_518400.sqlite")
JSON_STAR = os.path.join(LUAN_DIR, "star_logic.json")
JSON_PAIR = os.path.join(LUAN_DIR, "star_interaction_logic.json")


def build_star_rows():
    rows = []
    for key in LOGIC_STARS:
        obj = star_logic(key, None)
        rows.append(obj)
    return rows


def build_pair_rows():
    rows = []
    for a, b in itertools.combinations(LOGIC_STARS, 2):
        obj = pair_logic(a, b)
        # Ghi thêm cụm tương tác để tra nhanh.
        obj["interaction_key"] = classify_interaction(a, b)[0]
        rows.append(obj)
    return rows


def write_json(star_rows, pair_rows):
    os.makedirs(LUAN_DIR, exist_ok=True)
    with open(JSON_STAR, "w", encoding="utf-8") as f:
        json.dump(star_rows, f, ensure_ascii=False, indent=2)
    with open(JSON_PAIR, "w", encoding="utf-8") as f:
        json.dump(pair_rows, f, ensure_ascii=False, indent=2)


def write_sqlite(star_rows, pair_rows):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS star_logic")
    cur.execute("""
        CREATE TABLE star_logic (
            id INTEGER PRIMARY KEY,
            star TEXT UNIQUE, name TEXT, grp TEXT, nature TEXT,
            tags TEXT, ban_chat TEXT, positive TEXT, negative TEXT
        )
    """)
    for i, r in enumerate(star_rows):
        cur.execute(
            "INSERT INTO star_logic (star,name,grp,nature,tags,ban_chat,positive,negative) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (r["star"], r["name"], r.get("group", ""), r["nature"],
             ",".join(r["tags"]), r["ban_chat"], r["positive"], r["negative"]),
        )

    cur.execute("DROP TABLE IF EXISTS star_interaction_logic")
    cur.execute("""
        CREATE TABLE star_interaction_logic (
            id INTEGER PRIMARY KEY,
            star_a TEXT, star_b TEXT, star_a_name TEXT, star_b_name TEXT,
            category TEXT, interaction TEXT, interaction_key TEXT,
            ban_chat TEXT, positive TEXT, negative TEXT, note TEXT,
            tags_a TEXT, tags_b TEXT
        )
    """)
    for i, r in enumerate(pair_rows):
        cur.execute(
            "INSERT INTO star_interaction_logic "
            "(star_a,star_b,star_a_name,star_b_name,category,interaction,interaction_key,"
            "ban_chat,positive,negative,note,tags_a,tags_b) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (r["star_a"], r["star_b"], r["star_a_name"], r["star_b_name"],
             r["category"], r["interaction"], r.get("interaction_key", ""),
             r["ban_chat"], r["positive"], r["negative"], r["note"],
             ",".join(r["tags_a"]), ",".join(r["tags_b"])),
        )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pair_a ON star_interaction_logic(star_a, star_b)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pair_key ON star_interaction_logic(interaction_key)")
    conn.commit()
    conn.close()


def main():
    star_rows = build_star_rows()
    pair_rows = build_pair_rows()
    write_json(star_rows, pair_rows)
    write_sqlite(star_rows, pair_rows)
    print(f"Đã tạo {len(star_rows):,} hồ sơ sao logic; {len(pair_rows):,} cặp tương tác.")
    print(f"  JSON star : {JSON_STAR}")
    print(f"  JSON pair : {JSON_PAIR}")
    print(f"  SQLite    : {DB_PATH} (star_logic, star_interaction_logic)")


if __name__ == "__main__":
    main()
