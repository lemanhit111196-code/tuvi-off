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
from scripts.luan_giai_objective import objective_for_star_cung  # noqa: E402
from scripts.star_knowledge_data import STAR_META  # noqa: E402

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


def star_cung_analysis_rows():
    """Tạo bảng phân tích khách quan 3 chiều cho mọi sao × mọi cung."""
    out = []
    for star_key in STAR_META:
        for cung_index in range(12):
            obj = objective_for_star_cung(star_key, cung_index)
            meta = STAR_META[star_key]
            out.append({
                "star_key": star_key,
                "star_name": meta["name"],
                "star_group": meta["group"],
                "nature": meta["nature"],
                "cung_index": cung_index,
                "cung_name": CUNG_PROFILE[cung_index][0],
                "ban_chat": obj["ban_chat"],
                "positive": obj["positive"],
                "negative": obj["negative"],
                "comparison": obj["comparison"],
            })
    return out


def write_json(rows_map):
    os.makedirs(LUAN_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows_map, f, ensure_ascii=False, indent=2)
    # Bảng phân tích 3 chiều (lớn hơn một chút) ghi riêng.
    with open(os.path.join(LUAN_DIR, "star_cung_analysis.json"), "w", encoding="utf-8") as f:
        json.dump(rows_map["star_cung_analysis"], f, ensure_ascii=False, indent=2)


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

    create_table(conn, "star_cung_analysis", """
        id INTEGER PRIMARY KEY, star_key TEXT, star_name TEXT, star_group TEXT,
        nature TEXT, cung_index INTEGER, cung_name TEXT,
        ban_chat TEXT, positive TEXT, negative TEXT, comparison TEXT
    """)
    for i, r in enumerate(rows_map["star_cung_analysis"]):
        cur.execute(
            "INSERT INTO star_cung_analysis "
            "(star_key,star_name,star_group,nature,cung_index,cung_name,ban_chat,positive,negative,comparison) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (r["star_key"], r["star_name"], r["star_group"], r["nature"],
             r["cung_index"], r["cung_name"], r["ban_chat"], r["positive"],
             r["negative"], r["comparison"]),
        )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sca_key ON star_cung_analysis(star_key)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sca_cung ON star_cung_analysis(cung_index)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sca_key_cung ON star_cung_analysis(star_key, cung_index)")
    conn.commit()
    conn.close()


def main():
    rows_map = {
        "main_star_profile": star_rows(),
        "cung_profile": cung_rows(),
        "cuc_profile": cuc_rows(),
        "tua_hoa_profile": hoa_rows(),
        "cach_rules": cach_rows(),
        "star_cung_analysis": star_cung_analysis_rows(),
    }
    write_json(rows_map)
    write_sqlite(rows_map)
    print("Đã tạo kho tri thức luận giải:")
    print(f"  JSON  : {JSON_PATH}")
    print(f"  SQLite: {DB_PATH} (bảng main_star_profile, cung_profile, cuc_profile, tua_hoa_profile, cach_rules, star_cung_analysis)")
    for k, v in rows_map.items():
        print(f"  - {k}: {len(v)} dòng")


if __name__ == "__main__":
    main()
