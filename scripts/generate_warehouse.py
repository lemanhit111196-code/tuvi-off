# -*- coding: utf-8 -*-
"""
generate_warehouse.py
=====================
Sinh toàn bộ kho dữ liệu **518.400 biến thể lá số Tử Vi** và chia ra các nhóm
dữ liệu có thể truy xuất:

  1. data/tuvi_518400.sqlite          : kho chính (bảng `charts` + chỉ mục).
  2. data/csv_by_cuc/tuvi_by_cuc_*.csv.gz
                                       : 5 nhóm CSV nén chia theo Ngũ Hành Cục.
  3. data/json_sample/tuvi_sample_5.json
                                       : 5 lá số mẫu để xem cấu trúc.
  4. data/metadata/groups.json        : bảng số lượng theo từng nhóm.

Cách chạy:
    python3 scripts/generate_warehouse.py

Tuỳ chọn (nên dùng để thử) :
    python3 scripts/generate_warehouse.py --limit 1000
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import sqlite3
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scripts.tuvi_engine as engine  # noqa: E402
from scripts.tuvi_engine import build_chart  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
CSV_CUC_DIR = os.path.join(DATA_DIR, "csv_by_cuc")
JSON_SAMPLE_DIR = os.path.join(DATA_DIR, "json_sample")
META_DIR = os.path.join(DATA_DIR, "metadata")
SQLITE_PATH = os.path.join(DATA_DIR, "tuvi_518400.sqlite")

TOTAL_CHARTS = 60 * 2 * 12 * 30 * 12  # 518.400

# Tên 12 cung theo vị trí địa bàn (0=Dần..11=Sửu) trong bản CSV chi tiết.
CUNG_LABEL_COLUMNS = [f"cung_label_{i}" for i in range(12)]

# Cột metadata + một số sao chính để tra cứu nhanh trong SQLite.
# Toàn bộ chi tiết (mọi sao) nằm trong các file CSV nén chia theo Cục.
CHART_META_COLUMNS = [
    "year_index", "year_can_index", "year_chi_index",
    "gender_code", "gender_label",
    "lunar_month", "lunar_day", "hour_index", "hour_label",
    "duong_nam", "am_nu", "vong_thuan", "hoa_thuan",
    "menh_cung", "menh_cung_label", "than_cung", "than_cung_label",
    "cuc_so", "cuc_hanh", "cuc",
    "menh_can_index", "menh_chi_index", "than_can_index", "than_chi_index",
    "lai_nhan_cung", "tu_vi_cung",
    "group_cuc", "group_tu_vi", "group_menh", "group_than",
    "group_nam", "group_gio", "group_thang", "group_gioi_tinh",
]

# Cột metadata phiên bản compact lưu trong SQLite (tất cả số nguyên).
# Tên tiếng Việt đầy đủ nằm ở CSV nén và bảng tra `metadata/dimensions.json`.
SQLITE_META_COLUMNS = [
    "year_index", "year_can_index", "year_chi_index",
    "gender_code",
    "lunar_month", "lunar_day", "hour_index",
    "duong_nam", "am_nu", "vong_thuan", "hoa_thuan",
    "menh_cung", "than_cung", "cuc_so",
    "menh_can_index", "menh_chi_index", "than_can_index", "than_chi_index",
    "lai_nhan_cung", "tu_vi_cung",
]

# Cột lưu trong SQLite (compact, index nhanh). Tất cả `pos_*` còn lại chỉ ở CSV.
SQLITE_EXTRA_COLUMNS = [
    "pos_tu_vi", "pos_thien_co", "pos_thai_duong", "pos_vu_khuc",
    "pos_thien_dong", "pos_liem_trinh", "pos_thien_phu", "pos_thai_am",
    "pos_tham_lang", "pos_cu_mon", "pos_thien_tuong", "pos_thien_luong",
    "pos_that_sat", "pos_pha_quan",
    "pos_van_xuong", "pos_van_khuc", "pos_loc_ton",
    "pos_hoa_tinh", "pos_linh_tinh",
]

# Chỉ đánh chỉ mục trên các nhóm truy vấn thường xuyên nhất (giữ file SQLite gọn).
GROUP_COLUMNS = [
    "year_index", "gender_code", "cuc_so",
    "menh_cung", "than_cung", "tu_vi_cung",
]
COMPOSITE_INDEXES = [
    ("cuc_so", "tu_vi_cung"),
    ("year_index", "cuc_so"),
    ("menh_cung", "tu_vi_cung"),
]


def ensure_dirs():
    for path in (DATA_DIR, CSV_CUC_DIR, JSON_SAMPLE_DIR, META_DIR):
        os.makedirs(path, exist_ok=True)


def infer_column_types(columns: list[str], sample: dict) -> dict[str, str]:
    types = {}
    for col in columns:
        val = sample.get(col)
        types[col] = "INTEGER" if isinstance(val, int) else "TEXT"
    return types


def build_table_sql(columns: list[str], col_types: dict[str, str]) -> str:
    col_defs = ", ".join(f'"{c}" {col_types[c]}' for c in columns)
    return f'CREATE TABLE IF NOT EXISTS charts (\n    "chart_id" INTEGER PRIMARY KEY,\n    {col_defs}\n);'


def index_sql(names: list[str]) -> list[str]:
    def name(base: str) -> str:
        clean = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in base)
        return f"idx_{clean}"

    sqls = []
    for col in names:
        sqls.append(f'CREATE INDEX IF NOT EXISTS {name(col)} ON charts("{col}");')
    for pair in COMPOSITE_INDEXES:
        cols = ", ".join(f'"{c}"' for c in pair)
        sqls.append(f'CREATE INDEX IF NOT EXISTS {name("_".join(pair))} ON charts({cols});')
    return sqls


def make_row(chart_id: int, year_index: int, month: int, day: int,
             hour_index: int, gender_code: int) -> dict:
    row = build_chart(year_index, month, day, hour_index, gender_code)
    row["chart_id"] = chart_id
    # Nhóm biến thể (gốc) đơn giản hoá để truy xuất.
    return row


def open_csv_writers() -> dict[int, object]:
    writers = {}
    for cuc in (2, 3, 4, 5, 6):
        path = os.path.join(CSV_CUC_DIR, f"tuvi_by_cuc_{cuc}.csv.gz")
        f = gzip.open(path, "wt", encoding="utf-8", newline="")
        writer = csv.writer(f)
        writers[cuc] = (f, writer)
    return writers


def write_csv_rows(writers, header, row, columns):
    writer = writers[row["cuc_so"]][1]
    writer.writerow([row.get("chart_id", "")] + [row.get(c, "") for c in columns])


def main():
    parser = argparse.ArgumentParser(description="Sinh kho 518.400 lá số tử vi.")
    parser.add_argument("--limit", type=int, default=0,
                        help="Chỉ sinh N bản ghi đầu (để thử, mặc định 0 = toàn bộ).")
    args = parser.parse_args()
    limit = args.limit or TOTAL_CHARTS
    limit = min(limit, TOTAL_CHARTS)

    ensure_dirs()

    t0 = time.time()
    print(f"Bắt đầu sinh {limit}/{TOTAL_CHARTS:,} lá số ...")

    # Lấy mẫu để suy đoán kiểu dữ liệu và cột.
    sample = build_chart(0, 1, 1, 0, 1)
    csv_columns = [*CHART_META_COLUMNS, *CUNG_LABEL_COLUMNS,
                   *[k for k in sample if k.startswith("pos_")]]
    sql_columns = [*SQLITE_META_COLUMNS, *SQLITE_EXTRA_COLUMNS]
    col_types = infer_column_types(sql_columns, sample)

    # Mở CSV nén (toàn bộ cột).
    writers = open_csv_writers()
    for cuc, (_, writer) in writers.items():
        writer.writerow(["chart_id", *csv_columns])

    write_limit = limit
    count = 0
    last_report = time.time()

    conn = sqlite3.connect(SQLITE_PATH)
    conn.execute("PRAGMA journal_mode=OFF")
    conn.execute("PRAGMA synchronous=OFF")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA cache_size=-65536")
    cur = conn.cursor()
    cur.execute(build_table_sql(sql_columns, col_types))

    insert_sql = f'INSERT INTO charts ("chart_id", {", ".join(chr(34) + c + chr(34) for c in sql_columns)}) VALUES ({", ".join("?" * (len(sql_columns) + 1))})'
    batch = []

    for year_index in range(60):
        for gender_code in (1, 0):
            for month in range(1, 13):
                for hour_index in range(12):
                    for day in range(1, 31):
                        if count >= write_limit:
                            break
                        r = make_row(count, year_index, month, day, hour_index, gender_code)
                        batch.append([r.get("chart_id")] + [r.get(c) for c in sql_columns])
                        write_csv_rows(writers, None, r, csv_columns)
                        count += 1
                        if len(batch) >= 5000:
                            cur.executemany(insert_sql, batch)
                            batch = []
                        if time.time() - last_report > 10:
                            print(f"  {count:,} / {write_limit:,} bản ghi ...")
                            last_report = time.time()
                    if count >= write_limit:
                        break
                if count >= write_limit:
                    break
            if count >= write_limit:
                break
        if count >= write_limit:
            break

    if batch:
        cur.executemany(insert_sql, batch)
    conn.commit()

    # Thêm chỉ mục sau khi dữ liệu đã vào (nhanh hơn).
    print("Tạo chỉ mục SQLite ...")
    for stmt in index_sql(GROUP_COLUMNS):
        cur.execute(stmt)
    conn.commit()

    # Thống kê.
    print("Tính thống kê nhóm ...")
    stats = {}
    if count == TOTAL_CHARTS:
        queries = [("tong_so_la_so", "SELECT COUNT(*) FROM charts")]
        for label, col in [
            ("theo_cuc_so", "cuc_so"),
            ("theo_vi_tri_tu_vi", "tu_vi_cung"),
            ("theo_cung_menh", "menh_cung"),
            ("theo_cung_than", "than_cung"),
            ("theo_nam_index", "year_index"),
            ("theo_thang", "lunar_month"),
            ("theo_gio", "hour_index"),
            ("theo_gioi_tinh", "gender_code"),
        ]:
            rows = cur.execute(f'SELECT "{col}", COUNT(*) FROM charts GROUP BY "{col}" ORDER BY "{col}"').fetchall()
            stats[label] = {str(k): v for k, v in rows}
        total = cur.execute("SELECT COUNT(*) FROM charts").fetchone()[0]
        stats["tong_so_la_so"] = total
    else:
        stats["note"] = f"Chỉ sinh {count} lá số (chế độ --limit)."

    meta_path = os.path.join(META_DIR, "groups.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "tong_so_quy_hoach": TOTAL_CHARTS,
            "tong_so_da_sinh": count,
            "thoi_gian_tao": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "nguon": "tuvi_engine.py (Bắc phái)",
            "nhom": stats,
        }, f, ensure_ascii=False, indent=2)

    # Bảng tra (dimension) để dịch chỉ số trong SQLite/CSV ra tên tiếng Việt.
    dimensions = {
        "can_names": engine.CAN_NAMES,
        "chi_cung_names": engine.CHI_NAMES_CUNG,
        "hour_names": engine.HOUR_NAMES,
        "cung_names": engine.CUNG_10,
        "sexagenary": engine.SEXAGENARY,
        "cuc_by_so": {str(k): v for k, v in engine.CUC_NAMES.items()},
        "cuc_hanh_by_so": {str(k): v for k, v in engine.CUC_HANH.items()},
        "chinh_tinh_names": engine.CHINH_TINH_NAMES,
        "trang_sinh_names": engine.TRANG_SINH_NAMES,
        "thai_tue_names": engine.THAI_TUE_NAMES,
        "loc_ton_names": engine.LOC_TON_NAMES,
        "hoa_loc_by_can": engine.HOA_LOC_BY_CAN,
        "hoa_quyen_by_can": engine.HOA_QUYEN_BY_CAN,
        "hoa_khoa_by_can": engine.HOA_KHOA_BY_CAN,
        "hoa_ky_by_can": engine.HOA_KY_BY_CAN,
        "star_ascii_key": engine.STAR_ASCII_KEY,
    }
    with open(os.path.join(META_DIR, "dimensions.json"), "w", encoding="utf-8") as f:
        json.dump(dimensions, f, ensure_ascii=False, indent=2)

    # Đóng CSV.
    for cuc, (f, _) in writers.items():
        f.close()

    # Manifest các partition: đường dẫn, số dòng, kích thước, SHA-256.
    manifest = {"tong_so_la_so": count, "partitions": []}
    for cuc in (2, 3, 4, 5, 6):
        path = os.path.join(CSV_CUC_DIR, f"tuvi_by_cuc_{cuc}.csv.gz")
        with open(path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        manifest["partitions"].append({
            "cuc_so": cuc,
            "file": os.path.relpath(path, ROOT),
            "bytes": os.path.getsize(path),
            "sha256": digest,
        })
    with open(os.path.join(META_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # Mẫu JSON.
    sample_json = []
    sample_count = 0
    for yearly in range(60):
        for g in (1, 0):
            for m in range(1, 13):
                for h in range(12):
                    for d in range(1, 31):
                        if sample_count >= 5:
                            break
                        r = make_row(sample_count, yearly, m, d, h, g)
                        sample_json.append(r)
                        sample_count += 1
                    if sample_count >= 5:
                        break
                if sample_count >= 5:
                    break
            if sample_count >= 5:
                break
        if sample_count >= 5:
            break
    with open(os.path.join(JSON_SAMPLE_DIR, "tuvi_sample_5.json"), "w", encoding="utf-8") as f:
        json.dump(sample_json, f, ensure_ascii=False, indent=2)

    conn.close()

    elapsed = time.time() - t0
    print(f"Xong. {count:,} lá số trong {elapsed:.1f} giây.")
    print(f"  SQLite    : {SQLITE_PATH}")
    print(f"  CSV nén   : {CSV_CUC_DIR}")
    print(f"  Metadata  : {meta_path}")


if __name__ == "__main__":
    main()
