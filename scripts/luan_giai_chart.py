# -*- coding: utf-8 -*-
"""
luan_giai_chart.py
==================
Sinh bài LUẬN GIẢI TỰ ĐỘNG (rule-based NLG, đọc "giống AI") cho một lá số trong
kho 518.400.

Kết hợp:
  - Kho lá số (data/csv_by_cuc/*.csv.gz)          : vị trí sao thực tế.
  - Kho sao-cung (bảng star_cung_knowledge)       : mô tả sao ở cung.
  - Kho tri thức luận giải (luan_giai_knowledge)  : hồ sơ chính tinh, cung, cục,
                                                    cách cục, quy tắc.

Các đầu ra:
  --format text | markdown | json

Ví dụ:
  python3 scripts/luan_giai_chart.py --chart-id 106920 --format markdown
  python3 scripts/luan_giai_chart.py --chart-id 106920 --format json
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
from scripts.luan_giai_knowledge import (  # noqa: E402
    CACH_RULES,
    CUC_PROFILE,
    CUNG_PROFILE,
    FIELDS,
    FIELD_VI,
    LUAN_RULES,
    STAR_PROFILE,
    TUA_HOA_PROFILE,
)
from scripts.tuvi_engine import SEXAGENARY  # noqa: E402
from scripts.luan_giai_objective import objective_for_star_cung  # noqa: E402
from scripts.luan_giai_integrated import (  # noqa: E402
    build_cung_analysis,
    build_cung_block,
    build_overview,
    cung_stars,
    _main_stars,
    _notable_phu,
    _join_names,
)
from scripts.star_combo_knowledge import relation  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "tuvi_518400.sqlite")
CSV_DIR = os.path.join(ROOT, "data", "csv_by_cuc")

CHI_NAMES = ["Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi",
             "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"]
CUNG_NAMES = [CUNG_PROFILE[i][0] for i in range(12)]
MAIN_STARS = [
    ("Tử Vi", "pos_tu_vi"), ("Thiên Cơ", "pos_thien_co"),
    ("Thái Dương", "pos_thai_duong"), ("Vũ Khúc", "pos_vu_khuc"),
    ("Thiên Đồng", "pos_thien_dong"), ("Liêm Trinh", "pos_liem_trinh"),
    ("Thiên Phủ", "pos_thien_phu"), ("Thái Âm", "pos_thai_am"),
    ("Tham Lang", "pos_tham_lang"), ("Cự Môn", "pos_cu_mon"),
    ("Thiên Tướng", "pos_thien_tuong"), ("Thiên Lương", "pos_thien_luong"),
    ("Thất Sát", "pos_that_sat"), ("Phá Quân", "pos_pha_quan"),
]
STAR_TO_KEY = {name: key for name, key in MAIN_STARS}
KEY_TO_STAR = {key: name for name, key in MAIN_STARS}


def load_chart(chart_id: int):
    conn = sqlite3.connect(DB_PATH)
    meta = conn.execute("SELECT cuc_so, menh_cung, than_cung, year_index, gender_code "
                        "FROM charts WHERE chart_id=?", (chart_id,)).fetchone()
    if meta is None:
        sys.exit(f"Không có chart_id {chart_id}")
    cuc, menh, than, year_index, gender = meta
    path = os.path.join(CSV_DIR, f"tuvi_by_cuc_{cuc}.csv.gz")
    row = None
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["chart_id"] == str(chart_id):
                row = r
                break
    if row is None:
        sys.exit(f"Không đọc được chart {chart_id}")

    sk = {}
    for r in conn.execute("SELECT star_key,cung_name,description FROM star_cung_knowledge"):
        sk[(r[0], r[1])] = r[2]
    conn.close()
    return row, menh, than, sk


def get(row, key):
    return int(row.get(key, -1)) if row.get(key) not in ("", None) else -1


def cung_of(row, menh, key):
    pos = get(row, key)
    return (pos - menh) % 12 if pos >= 0 else None


def star_name_key(key):
    return KEY_TO_STAR.get(key, key)


def main_star_names_at_cung(row, menh, cuong_index):
    out = []
    for name, key in MAIN_STARS:
        if cung_of(row, menh, key) == cuong_index:
            out.append((name, key))
    return out


def profile_text(key):
    # `key` có thể là "pos_tu_vi" (từ MAIN_STARS) hoặc "tu_vi".
    k = key[4:] if key.startswith("pos_") else key
    return STAR_PROFILE.get(k, {})


def build_summary(row, menh, than):
    cuc_so = get(row, "cuc_so")
    cuc_name = row.get("cuc") if row.get("cuc") else CUC_PROFILE.get(cuc_so, {}).get("cuc_name", "?")
    sex = "Nam" if row.get("gender_code") == "1" else "Nữ"
    year_can_chi = row.get("year_can_chi") or SEXAGENARY[get(row, "year_index")]
    lines = []
    lines.append(f"- **Ngày sinh âm lịch:** {year_can_chi} năm "
                 f"(year_index {row.get('year_index')}), tháng {row.get('lunar_month')}, "
                 f"ngày {row.get('lunar_day')}, giờ {row.get('hour_label','')}.")
    lines.append(f"- **Giới tính:** {sex}.")
    lines.append(f"- **Mệnh tại {CHI_NAMES[menh]}** (cung **Mệnh**), "
                 f"**Thân tại {CHI_NAMES[than]}** (cung **{CUNG_NAMES[(than - menh) % 12]}**).")
    lines.append(f"- **Cục:** {cuc_name} (số {cuc_so}).")
    lines.append(f"- **Sao Tử Vi:** {CHI_NAMES[get(row,'tu_vi_cung')] if get(row,'tu_vi_cung')>=0 else '?'}.")
    return lines, cuc_name


def build_menh_than(row, menh, than, sk):
    lines = []
    menh_stars = main_star_names_at_cung(row, menh, 0)
    than_stars = main_star_names_at_cung(row, menh, (than - menh) % 12)
    lines.append("**Cung Mệnh** — nền tảng tính cách và bản mệnh.")
    if menh_stars:
        for name, key in menh_stars:
            p = profile_text(key)
            k = key[4:] if key.startswith("pos_") else key
            lines.append(f"- **{name}** thủ Mệnh: {p.get('tinh_cach','')} {sk.get((k, 'Mệnh'), '')}")
    else:
        lines.append("- Cung Mệnh không có chính tinh thủ — cần xem phụ tinh và sao hội chiếu.")
    lines.append("")
    lines.append("**Cung Thân** — hoạt động thực tế và giai đoạn trưởng thành.")
    if than == menh:
        lines.append("- Thân cư Mệnh: bản thân và việc làm gắn chặt; thành bại do tự mình quyết.")
    else:
        for name, key in than_stars:
            p = profile_text(key)
            lines.append(f"- **{name}** tại Thân: {p.get('su_nghiep','')}")
    return lines


def build_cung_profile(row, menh, sk):
    lines = []
    for cung_index in range(12):
        cung_name = CUNG_NAMES[cung_index]
        domain = CUNG_PROFILE[cung_index][1]
        stars = main_star_names_at_cung(row, menh, cung_index)
        if not stars:
            continue
        lines.append(f"### {cung_name} — {domain}")
        for name, key in stars:
            p = profile_text(key)
            k = key[4:] if key.startswith("pos_") else key
            desc = sk.get((k, cung_name), "")
            lines.append(f"**{name}**: {desc}")
            if cung_index in (4, 8, 10):
                lines.append(f"- Sự nghiệp: {p.get('su_nghiep','')}")
                lines.append(f"- Tài lộc: {p.get('tai_loc','')}")
                lines.append(f"- Tình duyên: {p.get('tinh_duyen','')}")
        lines.append("")
    return lines


def build_hoa(row, menh):
    lines = []
    hoa_map = [
        ("hoa_loc", "pos_hoa_loc", "Hóa Lộc"),
        ("hoa_quyen", "pos_hoa_quyen", "Hóa Quyền"),
        ("hoa_khoa", "pos_hoa_khoa", "Hóa Khoa"),
        ("hoa_ky", "pos_hoa_ky", "Hóa Kỵ"),
    ]
    for key, col, name in hoa_map:
        pos = get(row, col)
        if pos < 0:
            continue
        cung_index = (pos - menh) % 12
        p = TUA_HOA_PROFILE[key]
        lines.append(f"**{name}** tại cung **{CUNG_NAMES[cung_index]}** "
                     f"({CHI_NAMES[pos]}): {p['good_field']}")
    return lines


def build_cach(row, menh, than, sk):
    lines = []
    menh_index = 0
    than_cung = (than - menh) % 12
    tu_vi_at_menh = cung_of(row, menh, "pos_tu_vi") == 0
    than_menh = than_cung == 0
    loc_ton_at_menh = cung_of(row, menh, "pos_loc_ton") == 0
    loc_ton_at_tai = cung_of(row, menh, "pos_loc_ton") == 8
    van_at_menh = (cung_of(row, menh, "pos_van_xuong") == 0 or
                   cung_of(row, menh, "pos_van_khuc") == 0)
    khoi_viet_menh = (cung_of(row, menh, "pos_thien_khoi") == 0 or
                      cung_of(row, menh, "pos_thien_viet") == 0)
    hoa_loc_menh = cung_of(row, menh, "pos_hoa_loc") == 0
    hoa_quyen_menh = cung_of(row, menh, "pos_hoa_quyen") == 0
    hoa_ky_menh = cung_of(row, menh, "pos_hoa_ky") == 0
    hoa_linh_menh = (cung_of(row, menh, "pos_hoa_tinh") == 0 or
                     cung_of(row, menh, "pos_linh_tinh") == 0)
    dao_hoa_phuthe = cung_of(row, menh, "pos_dao_hoa") == 10
    cu_mon_menh = cung_of(row, menh, "pos_cu_mon") == 0

    conditions = {
        "TUVITHUMENH": tu_vi_at_menh,
        "THAN_CU_MENH": than_menh,
        "THAN_CU_QUAN": than_cung == 4,
        "LOC_TAI_MENH": loc_ton_at_menh,
        "LOC_TAI_TAI": loc_ton_at_tai,
        "VAN_XUONG_MENH": van_at_menh,
        "KHOI_VIET_MENH": khoi_viet_menh,
        "HOA_LOC_MENH": hoa_loc_menh,
        "HOA_QUYEN_MENH": hoa_quyen_menh,
        "HOA_KY_MENH": hoa_ky_menh,
        "HOA_LINH_MENH": hoa_linh_menh,
        "DAO_THOA_PHU_THE": dao_hoa_phuthe,
        "CU_MON_MENH": cu_mon_menh,
    }

    # Vũ Tham / Phủ Tướng / Sát Phá đồng cung.
    # Đơn giản hoá: tìm cung chứa cặp.
    for name_a, key_a in MAIN_STARS:
        for name_b, key_b in MAIN_STARS:
            if key_a >= key_b:
                continue
            ca = cung_of(row, menh, key_a)
            cb = cung_of(row, menh, key_b)
            if ca is not None and ca == cb:
                if {"pos_vu_khuc", "pos_tham_lang"} <= {key_a, key_b}:
                    conditions["THAM_VU_DONG"] = True
                if {"pos_thien_phu", "pos_thien_tuong"} <= {key_a, key_b}:
                    conditions["PHU_TUONG"] = True
                if {"pos_that_sat", "pos_pha_quan"} <= {key_a, key_b}:
                    conditions["SAT_PHA"] = True
    conditions.setdefault("THAM_VU_DONG", False)
    conditions.setdefault("PHU_TUONG", False)
    conditions.setdefault("SAT_PHA", False)

    for rule in CACH_RULES:
        if conditions.get(rule["ma"]):
            lines.append(f"- **{rule['ten']}**: {rule['desc']}")
    if not lines:
        lines.append("- Không có cách cục đặc biệt nào nổi bật; lá số thuộc dạng tương đối bình thường.")
    return lines


def build_advice(row, menh, than):
    lines = []
    loc_ton_tai = cung_of(row, menh, "pos_loc_ton") == 8
    hoa_ky_menh = cung_of(row, menh, "pos_hoa_ky") == 0
    that_sat_menh = cung_of(row, menh, "pos_that_sat") == 0
    cu_mon_menh = cung_of(row, menh, "pos_cu_mon") == 0
    if loc_ton_tai:
        lines.append("- Ưu tiên tích luỹ tài sản bền vững, đầu tư dài hạn.")
    if hoa_ky_menh:
        lines.append("- Dành thời gian chăm sóc tinh thần, giảm áp lực, tránh ôm đồm.")
    if that_sat_menh:
        lines.append("- Kiểm soát nóng nảy, hoãn quyết định lớn khi đang xúc động.")
    if cu_mon_menh:
        lines.append("- Cẩn ngôn để tránh thị phi; dùng khả năng nói chuyện vào việc tốt.")
    lines += list(LUAN_RULES[:4])
    return lines


def generate(chart_id: int):
    row, menh, than, sk = load_chart(chart_id)
    summary, cuc_name = build_summary(row, menh, than)

    md = []
    md.append(f"# Luận giải lá số `{chart_id}`")
    md.append("")
    md.append("> Bài luận giải sinh tự động từ kho tri thức Tử Vi (rule-based NLG). "
              "Mang tính tham khảo, không phải kết luận tuyệt đối.")
    md.append("")
    md.append("## 1. Thông tin lá số")
    md.append("")
    md += summary
    md.append("")
    md.append("## 2. Tổng quan liên kết (Mệnh – Thân và trục chính)")
    md.append("")
    md += build_overview(row, menh, than)
    md.append("## 3. Mệnh và Thân (liên kết chính tinh + phụ tinh)")
    md.append("")
    # Mệnh (cung 0) + Thân (nếu khác Mệnh).
    md += build_cung_block(row, menh, 0)
    than_cung = (than - menh) % 12
    if than_cung != 0:
        md += build_cung_block(row, menh, than_cung)
    md.append("## 4. Phân tích 12 cung (liên kết chính tinh + phụ tinh)")
    md.append("")
    md += build_cung_analysis(row, menh, skip={0, than_cung})
    md.append("## 5. Tứ Hoá")
    md.append("")
    md += build_hoa(row, menh)
    md.append("")
    md.append("## 6. Cách cục nổi bật")
    md.append("")
    md += build_cach(row, menh, than, sk)
    md.append("")
    md.append("## 7. Bản chất, ưu điểm và hạn chế/tiêu cực (chi tiết từng sao)")
    md.append("")
    md.append("> Phần này cố gắng nói đúng bản chất: nêu cả mặt mạnh lẫn mặt yếu, "
              "không nói giảm, không nói tránh. Kết luận cuối vẫn phụ thuộc cách cục "
              "và các sao hội chiếu.")
    md.append("")
    md += build_objective_analysis(row, menh)
    md.append("## 8. Tổ hợp sao nổi bật (biến thể khi các sao kết hợp)")
    md.append("")
    md.append("> Chỉ nêu các cặp sao có nội dung trong kho tri thức tổ hợp. Vị trí "
              "cùng cung / tam hợp / xung chiếu được xác định qua toạ độ cung thực tế.")
    md.append("")
    combo_lines = build_combo_analysis(row, menh)
    md += combo_lines if combo_lines else [
        "- Không phát hiện tổ hợp sao nổi bật nào trong các cặp đã ghi nhận."
    ]
    md.append("## 9. Gợi ý cuộc sống")
    md.append("")
    md += build_advice(row, menh, than)
    md.append("")
    md.append("## Nguồn")
    md.append("")
    md.append("- Kho lá số: `data/csv_by_cuc/*.csv.gz`")
    md.append("- Kho sao-cung: `star_cung_knowledge`")
    md.append("- Kho luận giải: `main_star_profile`, `cung_profile`, `cuc_profile`, `tua_hoa_profile`, `cach_rules`")
    md.append("- Tham khảo: `docs/nguon-algorithm.md`, `docs/star-kien-thuc-sao-o-cung.md`")

    text = "\n".join(md)
    obj = {
        "chart_id": chart_id,
        "summary": "\n".join(summary),
        "menh": f"{CHI_NAMES[menh]} - {CUNG_NAMES[0]}",
        "than": f"{CHI_NAMES[than]} - {CUNG_NAMES[(than - menh) % 12]}",
        "cuc": cuc_name,
        "sections": {
            "overview": build_overview(row, menh, than),
            "menh_than": build_menh_than(row, menh, than, sk),
            "cung_integrated": build_cung_analysis(row, menh, skip={0, than_cung}),
            "cung_profile": build_cung_profile(row, menh, sk),
            "tu_hoa": build_hoa(row, menh),
            "cach": build_cach(row, menh, than, sk),
            "objective": build_objective_analysis(row, menh),
            "combos": build_combo_analysis(row, menh),
            "advice": build_advice(row, menh, than),
        },
    }
    return text, obj


def main():
    p = argparse.ArgumentParser(description="Sinh luận giải giống AI cho một lá số.")
    p.add_argument("--chart-id", type=int, required=True)
    p.add_argument("--format", choices=["text", "markdown", "json"], default="markdown")
    a = p.parse_args()
    text, obj = generate(a.chart_id)
    if a.format == "json":
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    elif a.format == "markdown":
        print(text)
    else:
        print(text)


# --------------------------------------------------------------------------- #
# Phân tích khách quan 3 chiều (Bản chất / Ưu điểm / Hạn chế - tiêu cực).
# --------------------------------------------------------------------------- #
OBJECTIVE_KEYS = [
    "pos_tu_vi", "pos_thien_co", "pos_thai_duong", "pos_vu_khuc",
    "pos_thien_dong", "pos_liem_trinh", "pos_thien_phu", "pos_thai_am",
    "pos_tham_lang", "pos_cu_mon", "pos_thien_tuong", "pos_thien_luong",
    "pos_that_sat", "pos_pha_quan",
    "pos_loc_ton", "pos_hoa_tinh", "pos_linh_tinh",
    "pos_van_xuong", "pos_van_khuc", "pos_kinh_duong", "pos_da_la",
    "pos_thien_khoi", "pos_thien_viet", "pos_dao_hoa",
    "pos_an_quang", "pos_thien_quy", "pos_tam_thai", "pos_bat_toa",
]
_OBJECTIVE_NAMES = {
    "pos_tu_vi": "Tử Vi", "pos_thien_co": "Thiên Cơ", "pos_thai_duong": "Thái Dương",
    "pos_vu_khuc": "Vũ Khúc", "pos_thien_dong": "Thiên Đồng", "pos_liem_trinh": "Liêm Trinh",
    "pos_thien_phu": "Thiên Phủ", "pos_thai_am": "Thái Âm", "pos_tham_lang": "Tham Lang",
    "pos_cu_mon": "Cự Môn", "pos_thien_tuong": "Thiên Tướng", "pos_thien_luong": "Thiên Lương",
    "pos_that_sat": "Thất Sát", "pos_pha_quan": "Phá Quân", "pos_loc_ton": "Lộc Tồn",
    "pos_hoa_tinh": "Hỏa Tinh", "pos_linh_tinh": "Linh Tinh",
    "pos_van_xuong": "Văn Xương", "pos_van_khuc": "Văn Khúc",
    "pos_kinh_duong": "Kình Dương", "pos_da_la": "Đà La",
    "pos_thien_khoi": "Thiên Khôi", "pos_thien_viet": "Thiên Việt",
    "pos_dao_hoa": "Đào Hoa", "pos_an_quang": "Ân Quang", "pos_thien_quy": "Thiên Quý",
    "pos_tam_thai": "Tam Thai", "pos_bat_toa": "Bát Tọa",
}


def star_star_key_from_poscol(col):
    return col[4:] if col.startswith("pos_") else col


def build_objective_analysis(row, menh):
    """Liệt kê các sao nổi bật trong lá số, mỗi sao nêu Bản chất/Ưu/Hạn chế."""
    lines = []
    seen = set()
    for col in OBJECTIVE_KEYS:
        k = star_star_key_from_poscol(col)
        if k in seen:
            continue
        pos = get(row, col)
        if pos < 0:
            continue
        cung_index = (pos - menh) % 12
        cung_name = CUNG_NAMES[cung_index]
        star_name = _OBJECTIVE_NAMES.get(col, k)
        obj = objective_for_star_cung(k, cung_index)
        seen.add(k)
        lines.append(f"### {star_name} — cung {cung_name} ({CHI_NAMES[pos]})")
        lines.append("")
        lines.append(f"**Bản chất:** {obj['ban_chat']}")
        lines.append("")
        lines.append(f"**Tích cực:** {obj['positive']}")
        lines.append("")
        lines.append(f"**Hạn chế / tiêu cực:** {obj['negative']}")
        lines.append("")
        if obj["comparison"]:
            lines.append(f"**Đánh giá cân bằng:** {obj['comparison']}")
            lines.append("")
    return lines


# --------------------------------------------------------------------------- #
# Phân tích tổ hợp / biến thể sao trong lá số.
# --------------------------------------------------------------------------- #
def build_combo_analysis(row, menh):
    """Phát hiện các tổ hợp sao trong lá số và nêu bản chất/tích cực/tiêu cực.

    Chỉ nêu các cặp thực sự liên quan trong lá số:
      - cặp ĐÃ VIẾT TAY (authored) xuất hiện cùng lá số, hoặc
      - cặp sinh-tự-động có quan hệ trực tiếp (cùng cung / tam hợp / xung chiếu).
    """
    conn = sqlite3.connect(DB_PATH)
    combo_rows = conn.execute(
        "SELECT star_a, star_b, star_a_name, star_b_name, category, ban_chat, "
        "positive, negative, note, source FROM star_combo_analysis").fetchall()
    conn.close()
    combo_map = {}
    for r in combo_rows:
        combo_map[(r[0], r[1])] = r

    pos_map = {}
    for col in OBJECTIVE_KEYS:
        p = get(row, col)
        if p >= 0:
            pos_map[star_star_key_from_poscol(col)] = p

    lines = []
    used = set()
    keys = list(pos_map.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            for ca, cb in ((a, b), (b, a)):
                if (ca, cb) not in combo_map or (ca, cb) in used:
                    continue
                r = combo_map[(ca, cb)]
                rel = relation(pos_map[ca], pos_map[cb])
                # Bỏ cặp sinh tự động không có quan hệ trực tiếp trong lá số.
                if r[9] == "synth" and rel == "không nối trực tiếp":
                    continue
                used.add((ca, cb)); used.add((cb, ca))
                lines.append(f"### {r[2]} + {r[3]} — [{r[4]}] ({rel})")
                lines.append("")
                lines.append(f"**Bản chất:** {r[5]}")
                lines.append("")
                lines.append(f"**Tích cực:** {r[6]}")
                lines.append("")
                lines.append(f"**Tiêu cực:** {r[7]}")
                lines.append("")
                if r[8]:
                    lines.append(f"**Lưu ý:** {r[8]}")
                    lines.append("")
                break
    return lines


if __name__ == "__main__":
    main()
