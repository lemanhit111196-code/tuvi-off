# -*- coding: utf-8 -*-
"""
query_star_knowledge.py
=======================
Truy xuất "kiến thức sao ở cung" và ghép với một lá số cụ thể trong kho 518.400.

Ví dụ:

  # Kiến thức 1 sao × 12 cung
  python3 scripts/query_star_knowledge.py --star tu_vi

  # Kiến thức 1 cung × tất cả sao (so với cung Mệnh, index 0..11)
  python3 scripts/query_star_knowledge.py --cung 6

  # Ghép lá số cụ thể: tất cả sao của chart + mô tả theo cung thực tế
  python3 scripts/query_star_knowledge.py --chart-id 106920

  # Xuất markdown để làm tài liệu
  python3 scripts/query_star_knowledge.py --chart-id 106920 --format md

Lưu ý: `cung_index` luôn là vị trí TƯƠNG ĐỐI so với cung Mệnh.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.star_knowledge_data import CUNG_NAMES, STAR_META  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "tuvi_518400.sqlite")
CSV_DIR = os.path.join(ROOT, "data", "csv_by_cuc")

CHI_NAMES = ["Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi",
             "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"]


def conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def load_chart(chart_id: int) -> tuple[dict, dict]:
    """Trả (row đầy đủ, knowledge lookup dict)."""
    c = conn()
    meta = c.execute("SELECT cuc_so, menh_cung FROM charts WHERE chart_id=?", (chart_id,)).fetchone()
    if meta is None:
        sys.exit(f"Không có chart_id {chart_id}")
    cuc, menh = meta[0], meta[1]
    # Đọc dòng full-detail từ partition đúng Cục.
    path = os.path.join(CSV_DIR, f"tuvi_by_cuc_{cuc}.csv.gz")
    row = None
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["chart_id"] == str(chart_id):
                row = r
                break
    if row is None:
        sys.exit(f"Không đọc được chart {chart_id} từ {path}")

    # Bản đồ kiến thức: key = (star_key, cung_index).
    kn = {}
    for r in c.execute(
        "SELECT star_key, star_name, star_group, nature, cung_index, cung_name, description "
        "FROM star_cung_knowledge"):
        kn[(r[0], r[4])] = r
    c.close()
    return row, kn, menh


def chart_star_list(row: dict, menh: int, kn):
    items = []
    for k, v in row.items():
        if not (k.startswith("pos_") and v not in ("", None)):
            continue
        star_key = k[4:]
        if star_key not in STAR_META:
            continue
        pos = int(v)
        cung_index = (pos - menh) % 12
        krow = kn.get((star_key, cung_index))
        items.append({
            "star_key": star_key,
            "star_name": krow[1] if krow else star_key,
            "star_group": krow[2] if krow else "",
            "nature": krow[3] if krow else "",
            "cung_index": cung_index,
            "cung_name": krow[5] if krow else CUNG_NAMES[cung_index],
            "pos": pos,
            "pos_name": CHI_NAMES[pos],
            "description": krow[6] if krow else "",
        })
    items.sort(key=lambda x: (x["cung_index"], x["star_key"]))
    return items


def cmd_star(star_key: str):
    c = conn()
    rows = c.execute(
        "SELECT cung_index, cung_name, star_name, nature, description "
        "FROM star_cung_knowledge WHERE star_key=? ORDER BY cung_index", (star_key,)).fetchall()
    c.close()
    if not rows:
        sys.exit(f"Không có sao: {star_key}")
    for idx, cung, name, nat, desc in rows:
        print(f"[{idx}] {cung} — {name} ({nat})")
        print(f"   {desc}")


def cmd_cung(cung_index: int):
    c = conn()
    rows = c.execute(
        "SELECT star_key, star_name, star_group, nature, description "
        "FROM star_cung_knowledge WHERE cung_index=? ORDER BY star_key", (cung_index,)).fetchall()
    c.close()
    print(f"Cung {CUNG_NAMES[cung_index]} — {len(rows)} sao có kiến thức:")
    for key, name, group, nat, desc in rows:
        print(f"- {name} ({group}, {nat}): {desc}")


def cmd_chart(chart_id: int, fmt: str):
    row, kn, menh = load_chart(chart_id)
    items = chart_star_list(row, menh, kn)

    info = {
        "chart_id": chart_id,
        "year": row.get("year_index"),
        "gender": row.get("gender_code"),
        "month": row.get("lunar_month"),
        "day": row.get("lunar_day"),
        "hour": row.get("hour_index"),
        "cuc_so": row.get("cuc_so"),
        "menh_cung": menh,
        "menh_chi": CHI_NAMES[menh],
    }

    if fmt == "json":
        print(json.dumps({"info": info, "stars": items}, ensure_ascii=False, indent=2))
        return

    if fmt == "md":
        lines = [f"# Sao ở 12 cung — chart `{chart_id}`\n"]
        lines.append(f"- Cục {row.get('cuc_so')}, Mệnh {CHI_NAMES[menh]}, tháng {row.get('lunar_month')}, ngày {row.get('lunar_day')}, giờ {row.get('hour_index')}.")
        lines.append("")
        current = None
        for it in items:
            if it["cung_index"] != current:
                current = it["cung_index"]
                lines.append(f"## {it['cung_name']}")
                lines.append("")
            lines.append(f"**{it['star_name']}** ({it['pos_name']}) — {it['nature']}")
            lines.append("")
            lines.append(it["description"])
            lines.append("")
        print("\n".join(lines))
        return

    print(json.dumps(info, ensure_ascii=False, indent=2))
    for it in items:
        print(f"{it['cung_name']:<9} {it['star_name']:<14} {CHI_NAMES[it['pos']]:<4} {it['nature']}")
        print(f"    {it['description']}")


def main():
    p = argparse.ArgumentParser(description="Kiến thức sao ở cung + ghép lá số.")
    p.add_argument("--star", help="Tên/mã sao (VD tu_vi).")
    p.add_argument("--cung", type=int, choices=range(12), help="Chỉ số cung 0..11.")
    p.add_argument("--chart-id", type=int, help="chart_id trong kho.")
    p.add_argument("--format", choices=["text", "json", "md"], default="text")
    a = p.parse_args()

    if a.star:
        cmd_star(a.star)
    elif a.cung is not None:
        cmd_cung(a.cung)
    elif a.chart_id is not None:
        cmd_chart(a.chart_id, a.format)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
