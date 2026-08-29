# -*- coding: utf-8 -*-
"""
build_luan_giai_knowledge.py
============================
Sinh "kho tri thức luận giải giống AI" từ `luan_giai_knowledge.py` và ghi vào:

  - data/luan_giai/luan_giai_knowledge.json
  - bảng luan_giai_* trong data/tuvi_518400.sqlite

Các bảng:
  - main_star_profile  : 14 chính tinh theo lĩnh vực.
  - cung_profile       : 12 cung.
  - cuc_profile        : 5 cục.
  - tua_hoa_profile    : Tứ Hoá.
  - cach_rules         : cách cục / quy tắc luận.

Chạy:
  python3 scripts/build_luan_giai_knowledge.py
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.luan_giai_knowledge import (  # noqa: E402
    CACH_RULES,
    CUC_PROFILE,
    CUNG_PROFILE,
    FIELD_VI,
    FIELDS,
    LUAN_RULES,
    STAR_PROFILE,
    TUA_HOA_PROFILE,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
LUAN_DIR = os.path.join(DATA_DIR, "luan_giai")
DB_PATH = os.path.join(DATA_DIR, "tuvi_518400.sqlite")
JSON_PATH = os.path.join(LUAN_DIR, "luan_giai_knowledge.json")


def star_rows():
    out = []
    for key, p in STAR_PROFILE.items():
        out.append({
            "star_key": key,
            "star_name": p["name"],
            "element": p["element"],
            "nature": p["nature"],
            "about": p["about"],
            **{f: p[f] for f in FIELDS},
            "note": p["note"],
        })
    return out


def cung_rows():
    out = []
    for idx, (name, domain, pos, neg, advice) in CUNG_PROFILE.items():
        out.append({
            "cung_index": idx,
            "cung_name": name,
            "domain": domain,
            "positive": pos,
            "negative": neg,
            "advice": advice,
        })
    return out


def cuc_rows():
    out = []
    for name, p in CUC_PROFILE.items():
        out.append({
            "cuc_so": p["so"],
            "cuc_name": name,
            "hanh": p["hanh"],
            "nature": p["nature"],
            "about": p["about"],
            "career": p["career"],
            "tai": p["tai"],
            "tinh": p["tinh"],
            "note": p["note"],
        })
    return out


def hoa_rows():
    out = []
    for key, p in TUA_HOA_PROFILE.items():
        out.append({
            "hoa_key": key,
            "hoa_name": p["name"],
            "meaning": p["meaning"],
            "good_field": p["good_field"],
        })
    return out


def cach_rows():
    out = []
    for r in CACH_RULES:
        out.append({
            "ma": r["ma"],
            "ten": r["ten"],
            "muc": r["muc"],
            "dieu_kien": r["condition"],
            "mo_ta": r["desc"],
        })
    for i, rule in enumerate(LUAN_RULES, start=1):
        out.append({
            "ma": f"RULE{i:03d}",
            "ten": f"Quy tắc {i}",
            "muc": "luận tổng hợp",
            "dieu_kien": "áp dụng mọi lá số",
            "mo_ta": rule,
        })
    return out


def write_json(rows_map):
    os.makedirs(LUAN_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows_map, f, ensure_ascii=False, indent=2)


def create_table(conn, name, columns):
    conn.execute(f"DROP TABLE IF EXISTS {name}")
    conn.execute(f"CREATE TABLE {name} ({columns})")


def write_sqlite(rows_map):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    create_table(conn, "main_star_profile", """
        star_key TEXT PRIMARY KEY, star_name TEXT, element TEXT, nature TEXT,
        about TEXT, tinh_cach TEXT, su_nghiep TEXT, tai_loc TEXT,
        tinh_duyen TEXT, suc_khoe TEXT, note TEXT
    """)
    for r in rows_map["main_star_profile"]:
        cur.execute(
            "INSERT INTO main_star_profile VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (r["star_key"], r["star_name"], r["element"], r["nature"], r["about"],
             r["tinh_cach"], r["su_nghiep"], r["tai_loc"], r["tinh_duyen"],
             r["suc_khoe"], r["note"]),
        )

    create_table(conn, "cung_profile", """
        cung_index INTEGER, cung_name TEXT, domain TEXT,
        positive TEXT, negative TEXT, advice TEXT
    """)
    for r in rows_map["cung_profile"]:
        cur.execute("INSERT INTO cung_profile VALUES (?,?,?,?,?,?)",
                    (r["cung_index"], r["cung_name"], r["domain"],
                     r["positive"], r["negative"], r["advice"]))

    create_table(conn, "cuc_profile", """
        cuc_so INTEGER, cuc_name TEXT, hanh TEXT, nature TEXT, about TEXT,
        career TEXT, tai TEXT, tinh TEXT, note TEXT
    """)
    for r in rows_map["cuc_profile"]:
        cur.execute("INSERT INTO cuc_profile VALUES (?,?,?,?,?,?,?,?,?)",
                    (r["cuc_so"], r["cuc_name"], r["hanh"], r["nature"],
                     r["about"], r["career"], r["tai"], r["tinh"], r["note"]))

    create_table(conn, "tua_hoa_profile", """
        hoa_key TEXT, hoa_name TEXT, meaning TEXT, good_field TEXT
    """)
    for r in rows_map["tua_hoa_profile"]:
        cur.execute("INSERT INTO tua_hoa_profile VALUES (?,?,?,?)",
                    (r["hoa_key"], r["hoa_name"], r["meaning"], r["good_field"]))

    create_table(conn, "cach_rules", """
        ma TEXT, ten TEXT, muc TEXT, dieu_kien TEXT, mo_ta TEXT
    """)
    for r in rows_map["cach_rules"]:
        cur.execute("INSERT INTO cach_rules VALUES (?,?,?,?,?)",
                    (r["ma"], r["ten"], r["muc"], r["dieu_kien"], r["mo_ta"]))

    conn.commit()
    conn.close()


def main():
    rows_map = {
        "main_star_profile": star_rows(),
        "cung_profile": cung_rows(),
        "cuc_profile": cuc_rows(),
        "tua_hoa_profile": hoa_rows(),
        "cach_rules": cach_rows(),
    }
    write_json(rows_map)
    write_sqlite(rows_map)
    print("Đã tạo kho tri thức luận giải:")
    print(f"  JSON  : {JSON_PATH}")
    print(f"  SQLite: {DB_PATH} (bảng main_star_profile, cung_profile, cuc_profile, tua_hoa_profile, cach_rules)")
    for k, v in rows_map.items():
        print(f"  - {k}: {len(v)} dòng")


if __name__ == "__main__":
    main()
