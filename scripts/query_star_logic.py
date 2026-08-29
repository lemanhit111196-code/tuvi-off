# -*- coding: utf-8 -*-
"""
query_star_logic.py
===================
Truy xuất hệ thống LOGIC LUẬN GIẢI SAO và TƯƠNG TÁC SAO.

Ví dụ:
  python3 scripts/query_star_logic.py --star tu_vi
  python3 scripts/query_star_logic.py --star thien_dong --cung 0
  python3 scripts/query_star_logic.py --pair tu_vi thien_phu
  python3 scripts/query_star_logic.py --list-pair --interaction cộng hung
  python3 scripts/query_star_logic.py --chart-id 106920
"""

from __future__ import annotations

import argparse
import sqlite3
import sys

DB_PATH = "data/tuvi_518400.sqlite"


def connect():
    return sqlite3.connect(DB_PATH)


def _norm(k):
    return k.strip().lower().replace("pos_", "")


def show_star(key, cung=None):
    c = connect()
    row = c.execute(
        "SELECT name, grp, nature, tags, ban_chat, positive, negative "
        "FROM star_logic WHERE star=?", (key,)).fetchone()
    c.close()
    if not row:
        sys.exit(f"Không có hồ sơ logic cho sao '{key}'.")
    name, grp, nature, tags, ban, pos, neg = row
    print(f"=== {name} — [nhóm: {grp}; thiên tính: {nature}] ===")
    print(f"Thẻ ngữ nghĩa: {tags}")
    print(f"Bản chất  : {ban}")
    print(f"Tích cực  : {pos}")
    print(f"Tiêu cực  : {neg}")
    if cung is not None:
        from scripts.star_logic_engine import star_logic
        obj = star_logic(key, cung)
        print("\n--- Theo cung ---")
        print(f"Bản chất tại cung {cung}: {obj['ban_chat']}")
        print(f"Tích cực:{obj['positive']}")
        print(f"Tiêu cực:{obj['negative']}")


def show_pair(a, b):
    c = connect()
    row = c.execute(
        "SELECT star_a_name, star_b_name, category, interaction, interaction_key, "
        "ban_chat, positive, negative, note FROM star_interaction_logic "
        "WHERE (star_a=? AND star_b=?) OR (star_a=? AND star_b=?)",
        (a, b, b, a)).fetchone()
    c.close()
    if not row:
        sys.exit(f"Không có cặp {a}/{b}.")
    name_a, name_b, cat, itype, ikey, ban, pos, neg, note = row
    print(f"=== {name_a} + {name_b} — [{cat}; {itype}] ===")
    print(f"Bản chất  : {ban}")
    print(f"Tích cực  : {pos}")
    print(f"Tiêu cực  : {neg}")
    print(f"Lưu ý     : {note}")


def list_pairs(interaction=None):
    c = connect()
    if interaction:
        rows = c.execute(
            "SELECT star_a_name, star_b_name, category, interaction FROM star_interaction_logic "
            "WHERE interaction LIKE ? ORDER BY star_a_name LIMIT 120",
            (f"%{interaction}%",)).fetchall()
    else:
        rows = c.execute(
            "SELECT star_a_name, star_b_name, category, interaction FROM star_interaction_logic "
            "ORDER BY star_a_name LIMIT 300").fetchall()
    c.close()
    for a, b, cat, itype in rows:
        print(f"{a} + {b}  [{cat} | {itype}]")


def chart_pairs(chart_id):
    import gzip
    import csv
    from scripts.luan_giai_chart import load_chart
    from scripts.star_logic_engine import chart_interactions
    row, menh, than, sk = load_chart(chart_id)
    items = chart_interactions(row, menh)
    print(f"=== Lá số {chart_id}: {len(items)} cặp sao trong chart (chỉ hiện quan hệ + nổi tiếng) ===")
    for it in items:
        if it["relation"] == "không nối trực tiếp" and it["category"] not in (
                "quyền-tài", "tài-dục", "đào-hoa", "âm-dương", "trí-phúc",
                "khẩu-tài", "văn-học", "quý-nhân", "phú-quý", "đại-phú"):
            continue
        print(f"- {it['star_a_name']} + {it['star_b_name']} [{it['category']} | {it['interaction']}] "
              f"({it['relation']}, cung {it['cung_a']}–{it['cung_b']})")


def main():
    p = argparse.ArgumentParser(description="Kho logic sao và tương tác sao.")
    p.add_argument("--star")
    p.add_argument("--cung", type=int)
    p.add_argument("--pair", nargs=2, metavar=("SAO_A", "SAO_B"))
    p.add_argument("--list-pair", action="store_true")
    p.add_argument("--interaction")
    p.add_argument("--chart-id", type=int)
    a = p.parse_args()
    if a.star:
        show_star(_norm(a.star), a.cung)
    elif a.pair:
        show_pair(_norm(a.pair[0]), _norm(a.pair[1]))
    elif a.list_pair:
        list_pairs(a.interaction)
    elif a.chart_id:
        chart_pairs(a.chart_id)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
