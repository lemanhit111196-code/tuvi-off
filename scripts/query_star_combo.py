# -*- coding: utf-8 -*-
"""
query_star_combo.py
===================
Truy xuất kho tri thức tổ hợp / biến thể sao.

Ví dụ:
  python3 scripts/query_star_combo.py --combo tu_vi thien_phu
  python3 scripts/query_star_combo.py --list
  python3 scripts/query_star_combo.py --search "Tử Vi"
"""

from __future__ import annotations

import argparse
import sqlite3
import sys

DB_PATH = "data/tuvi_518400.sqlite"


def connect():
    return sqlite3.connect(DB_PATH)


def show_one(pair):
    c = connect()
    rows = c.execute(
        "SELECT star_a_name, star_b_name, category, ban_chat, positive, negative, note "
        "FROM star_combo_analysis WHERE (star_a=? AND star_b=?) OR (star_a=? AND star_b=?)",
        (pair[0], pair[1], pair[1], pair[0]),
    ).fetchall()
    c.close()
    if not rows:
        sys.exit("Không có tổ hợp này.")
    for a, b, cat, ban, pos, neg, note in rows:
        print(f"=== {a} + {b} — [{cat}] ===")
        print(f"Bản chất  : {ban}")
        print(f"Tích cực  : {pos}")
        print(f"Tiêu cực  : {neg}")
        print(f"Lưu ý     : {note}")


def show_list():
    c = connect()
    rows = c.execute(
        "SELECT star_a_name, star_b_name, category FROM star_combo_analysis ORDER BY star_a_name, star_b_name"
    ).fetchall()
    c.close()
    for a, b, cat in rows:
        print(f"{a} + {b}  [{cat}]")


def show_search(q):
    c = connect()
    rows = c.execute(
        "SELECT star_a_name, star_b_name, category, ban_chat FROM star_combo_analysis "
        "WHERE star_a_name LIKE ? OR star_b_name LIKE ? OR ban_chat LIKE ? ORDER BY star_a_name",
        (f"%{q}%", f"%{q}%", f"%{q}%"),
    ).fetchall()
    c.close()
    for a, b, cat, ban in rows:
        print(f"{a} + {b}  [{cat}]")
        print(f"   {ban}")


def main():
    p = argparse.ArgumentParser(description="Kho tri thức tổ hợp sao.")
    p.add_argument("--combo", nargs=2, metavar=("SAO_A", "SAO_B"))
    p.add_argument("--list", action="store_true")
    p.add_argument("--search")
    a = p.parse_args()
    if a.combo:
        show_one(a.combo)
    elif a.search:
        show_search(a.search)
    else:
        show_list()


if __name__ == "__main__":
    main()
