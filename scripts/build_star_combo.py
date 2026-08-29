# -*- coding: utf-8 -*-
"""
build_star_combo.py
===================
Sinh bảng tri thức **TỔ HỢP SAO** vào kho.

Nội dung:
  - 40+ tổ hợp được viết tay trong `scripts/star_combo_knowledge.py`.
  - Toàn bộ cặp 14 chính tinh (91 cặp) được sinh bản chất/tích cực/tiêu cực từ
    hồ sơ hai sao (main_star_profile) + tính chất cung.

Đầu ra:
  - data/luan_giai/star_combo_analysis.json
  - bảng `star_combo_analysis` trong data/tuvi_518400.sqlite

Chạy:
  python3 scripts/build_star_combo.py
"""

from __future__ import annotations

import itertools
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.luan_giai_knowledge import STAR_PROFILE, CUNG_PROFILE  # noqa: E402
from scripts.star_combo_knowledge import COMBO_DATA, relation  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
LUAN_DIR = os.path.join(DATA_DIR, "luan_giai")
DB_PATH = os.path.join(DATA_DIR, "tuvi_518400.sqlite")
JSON_PATH = os.path.join(LUAN_DIR, "star_combo_analysis.json")

MAIN_KEYS = list(STAR_PROFILE.keys())  # 14 chính tinh

# Tên đầy đủ cho các phụ tinh / tứ hoá xuất hiện trong COMBO_DATA nhưng không
# nằm trong STAR_PROFILE (main_star_profile).
_STAR_NAME_MAP = {
    "loc_ton": "Lộc Tồn",
    "kinh_duong": "Kình Dương",
    "da_la": "Đà La",
    "hoa_tinh": "Hỏa Tinh",
    "linh_tinh": "Linh Tinh",
    "van_xuong": "Văn Xương",
    "van_khuc": "Văn Khúc",
    "thien_khoi": "Thiên Khôi",
    "thien_viet": "Thiên Việt",
    "dao_hoa": "Đào Hoa",
    "hong_loan": "Hồng Loan",
    "thien_ma": "Thiên Mã",
    "hoa_loc": "Hóa Lộc",
    "hoa_quyen": "Hóa Quyền",
    "hoa_khoa": "Hóa Khoa",
    "hoa_ky": "Hóa Kỵ",
    "thai_am": "Thái Âm",
    "thien_luong": "Thiên Lương",
    "liem_trinh": "Liêm Trinh",
}


def _name(key: str) -> str:
    """Tên sao đầy đủ, ưu tiên main_star_profile, fallback map, fallback khoá."""
    if key in STAR_PROFILE:
        return STAR_PROFILE[key]["name"]
    return _STAR_NAME_MAP.get(key, key)


def _career_short(star_key):
    """Rút gọn 'Hợp ...' thành lĩnh vực ngắn sau chữ 'Hợp'."""
    s = STAR_PROFILE[star_key].get("su_nghiep", "")
    s = s.replace("Hợp", "", 1).strip()
    return s.split(";")[0].strip()


def _synth(pair, rel):
    a, b = pair
    pa, pb = STAR_PROFILE[a], STAR_PROFILE[b]
    nature_a = "tốt" if pa["nature"] in ("cát", "cát-hung") else "xấu"
    nature_b = "tốt" if pb["nature"] in ("cát", "cát-hung") else "xấu"
    if nature_a == nature_b == "tốt":
        tone = "hai cát tinh — hợp nhau, tăng lực"
        positive = ("Cả hai đều thuộc nhóm tốt: kết hợp có lợi cho ổn định, công danh, "
                    "được giúp đỡ, dễ đạt kết quả khi gặp đúng cung.")
        negative = ("Vẫn có mặt yếu: dễ tự mãn, chủ quan; nếu hai sao đều đắc có thể sinh kỳ vọng "
                    "quá cao, thiếu người góp ý sẽ chậm nhận ra sai lầm.")
    elif nature_a == "xấu" and nature_b == "xấu":
        tone = "hai hung tinh — tăng hung / xung khắc"
        positive = ("Không phải chỉ có hại: biết rõ rủi ro giúp chủ động phòng, rèn nghị lực, "
                    "tránh tự mãn.")
        negative = ("Đây là nhóm rủi ro thật: dễ tổn thất, thị phi, căng thẳng, bệnh tật, "
                    "gặp chuyện liên quan đến cung đóng nếu không kiểm soát.")
    else:
        tone = "cát tinh gặp hung tinh — cần cân bằng"
        positive = ("Sao tốt làm nền, tạo cơ hội tiến thân; sao xấu buộc phải rèn kỷ luật, "
                    "thận trọng và học bài học.")
        negative = ("Ảnh hưởng xấu vẫn có thật: dễ bị kéo lệch, cản trở, thất bại một phần "
                    "nếu không tỉnh táo và không chuẩn bị.")
    ban_chat = (
        f"Tổ hợp {pa['name']} + {pb['name']} ({rel}): bản chất là {pa['name']} {pa['tinh_cach'].lower()} "
        f"gặp {pb['name']} {pb['tinh_cach'].lower()}. Nhìn chung đây là {tone}."
    )
    return {
        "ban_chat": ban_chat,
        "positive": positive,
        "negative": negative,
        "note": f"Đánh giá theo đắc/hãm và cung đóng: {pa['name']} hợp {_career_short(a)}; "
                f"{pb['name']} hợp {_career_short(b)}.",
        "category": tone,
    }


def build_rows():
    rows = []
    for (a, b), obj in COMBO_DATA.items():
        rows.append({
            "star_a": a,
            "star_b": b,
            "star_a_name": _name(a),
            "star_b_name": _name(b),
            "category": obj.get("category", "tổ hợp"),
            "ban_chat": obj["ban_chat"],
            "positive": obj["positive"],
            "negative": obj["negative"],
            "note": obj.get("note", ""),
            "source": "authored",
        })
    # Sinh cặp còn thiếu trong 14 chính tinh.
    existing = {(r["star_a"], r["star_b"]) for r in rows}
    for a, b in itertools.combinations(MAIN_KEYS, 2):
        if (a, b) in existing or (b, a) in existing:
            continue
        obj = _synth((a, b), "không ghi rõ quan hệ")
        rows.append({
            "star_a": a,
            "star_b": b,
            "star_a_name": _name(a),
            "star_b_name": _name(b),
            "category": obj["category"],
            "ban_chat": obj["ban_chat"],
            "positive": obj["positive"],
            "negative": obj["negative"],
            "note": obj["note"],
            "source": "synth",
        })
    return rows


def write_json(rows):
    os.makedirs(LUAN_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


def write_sqlite(rows):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS star_combo_analysis")
    cur.execute("""
        CREATE TABLE star_combo_analysis (
            id INTEGER PRIMARY KEY,
            star_a TEXT, star_b TEXT,
            star_a_name TEXT, star_b_name TEXT,
            category TEXT,
            ban_chat TEXT, positive TEXT, negative TEXT, note TEXT,
            source TEXT
        )
    """)
    for i, r in enumerate(rows):
        cur.execute(
            "INSERT INTO star_combo_analysis "
            "(star_a,star_b,star_a_name,star_b_name,category,ban_chat,positive,negative,note,source) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (r["star_a"], r["star_b"], r["star_a_name"], r["star_b_name"],
             r["category"], r["ban_chat"], r["positive"], r["negative"],
             r["note"], r["source"]),
        )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_combo_a ON star_combo_analysis(star_a, star_b)")
    conn.commit()
    conn.close()


def main():
    rows = build_rows()
    write_json(rows)
    write_sqlite(rows)
    print(f"Đã tạo {len(rows):,} tổ hợp sao.")
    print(f"  JSON  : {JSON_PATH}")
    print(f"  SQLite: {DB_PATH} (bảng star_combo_analysis)")


if __name__ == "__main__":
    main()
