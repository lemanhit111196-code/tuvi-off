# -*- coding: utf-8 -*-
"""
luan_giai_integrated.py
=======================
Tầng LUẬN GIẢI LIÊN KẾT: đọc lá số theo CUNG, tại mỗi cung gom tất cả
chính tinh + phụ tinh + bộ sao, rồi viết thành một đoạn liền mạch:

  - Bản chất liên kết : chính tinh định hình cung, phụ tinh làm mạnh/yếu.
  - Điểm mạnh        : gộp mặt tích cực của chính tinh và phụ tinh tốt.
  - Điểm yếu / cẩn trọng : gộp mặt hạn chế của chính tinh và phụ tinh xấu.

Mục tiêu: khắc phục kiểu luận "liệt kê từng sao rời rạc" bằng cách biến
các sao trong cùng một cung thành một bức tranh có liên kết.
"""

from __future__ import annotations

from scripts.luan_giai_knowledge import CUNG_PROFILE, STAR_PROFILE
from scripts.luan_giai_objective import objective_for_star_cung
from scripts.star_knowledge_data import STAR_META

# 14 chính tinh theo thứ tự thường dùng.
MAIN_KEYS = [
    "tu_vi", "thien_co", "thai_duong", "vu_khuc", "thien_dong", "liem_trinh",
    "thien_phu", "thai_am", "tham_lang", "cu_mon", "thien_tuong",
    "thien_luong", "that_sat", "pha_quan",
]
MAIN_SET = set(MAIN_KEYS)

# Phụ tinh có ảnh hưởng rõ trong luận giải (được ưu tiên nhắc tên khi gom cung).
NOTABLE_PHU = {
    "loc_ton", "kinh_duong", "da_la", "hoa_tinh", "linh_tinh",
    "van_xuong", "van_khuc", "thien_khoi", "thien_viet", "dao_hoa",
    "thien_ma", "ta_phu", "huu_bat", "thai_phu", "phong_cao",
    "thien_quang", "thien_phuc", "thien_tru", "quang_an_can",
    "long_tri", "phuong_cac", "giai_than", "thien_duc", "nguyet_duc",
    "hong_loan", "thien_hy", "co_than", "qua_tu", "hoa_cai",
    "thien_khong", "dia_khong", "dia_kiep", "thien_hinh", "thien_dieu",
    "thien_y", "thien_giai", "dia_giai", "thien_tai", "thien_tho",
    "thien_khoc", "thien_hu", "kiep_sat", "pha_toai", "an_quang",
    "thien_quy", "tam_thai", "bat_toa",
    "thien_la", "dia_vong", "thien_thuong", "thien_su", "dau_quan",
    "hoa_loc", "hoa_quyen", "hoa_khoa", "hoa_ky",
}

RING_GROUPS = ("vòng Trường Sinh", "vòng Thái Tuế", "vòng Lộc Tồn")

# 12 chi theo toạ độ cung 0..11 = Dần..Sửu (giống tuvi_engine).
CHI_NAMES = ["Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi",
             "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"]


def _name(key: str) -> str:
    meta = STAR_META.get(key)
    if meta:
        return meta["name"]
    return STAR_PROFILE.get(key, {}).get("name", key)


def _nature(key: str) -> str:
    return STAR_META.get(key, {}).get("nature", "trung")


def _group(key: str) -> str:
    return STAR_META.get(key, {}).get("group", "")


def _short(text: str, limit: int = 130) -> str:
    """Rút gọn (cắt theo khoảng trắng) và bỏ dấu thừa ở cuối để ghép câu mượt hơn."""
    text = text.strip()
    if len(text) > limit:
        cut = text[:limit]
        sp = cut.rfind(" ")
        if sp > 40:
            cut = cut[:sp]
        text = cut.rstrip() + "…"
    return text.rstrip(" .;:")


def cung_stars(row, menh: int, cung_index: int):
    """Trả về danh sách sao nằm tại một cung (vị trí thực tế từ cột pos_*)."""
    out = []
    for col, val in row.items():
        if not col.startswith("pos_") or val in ("", None, "-1"):
            continue
        try:
            pos = int(val)
        except (TypeError, ValueError):
            continue
        if (pos - menh) % 12 != cung_index:
            continue
        key = col[4:]
        obj = objective_for_star_cung(key, cung_index)
        out.append({
            "key": key,
            "name": _name(key),
            "nature": _nature(key),
            "group": _group(key),
            "obj": obj,
        })
    # Chính tinh trước, phụ tinh theo thứ tự xuất hiện.
    out.sort(key=lambda s: (0 if s["key"] in MAIN_SET else 1,
                            MAIN_KEYS.index(s["key"]) if s["key"] in MAIN_SET else 99))
    return out


def _main_stars(stars):
    return [s for s in stars if s["key"] in MAIN_SET]


def _notable_phu(stars):
    return [s for s in stars if s["key"] not in MAIN_SET and s["key"] in NOTABLE_PHU]


def _rings(stars):
    out = {}
    for s in stars:
        g = s["group"]
        if g in RING_GROUPS:
            out.setdefault(g, []).append(s["name"])
    return out


def _join_names(items, limit=5):
    names = [i["name"] for i in items[:limit]]
    if not names:
        return ""
    if len(items) > limit:
        return ", ".join(names) + f" (+{len(items) - limit})"
    return ", ".join(names)


def _synthesize_cung(stars, cung_index):
    """Sinh đoạn văn liên kết cho một cung."""
    main = _main_stars(stars)
    phu = _notable_phu(stars)
    rings = _rings(stars)

    good_phu = [s for s in phu if s["nature"] in ("tốt", "cát")]
    bad_phu = [s for s in phu if s["nature"] in ("xấu", "xấu-trung")]
    neu_phu = [s for s in phu if s["nature"] == "trung"]

    cung_name, _, cpos, cneg, _ = CUNG_PROFILE[cung_index]

    # ---- Bản chất liên kết ----
    if main:
        core = "; ".join(_short(s["obj"]["ban_chat"], 110) for s in main[:2])
        ban = f"Chính tinh {_join_names(main, 3)} định hình cung này: {core}."
    else:
        ban = (f"Cung {cung_name} không có chính tinh đóng, nội dung chủ yếu do phụ tinh và bộ sao tạo nên. "
               f"Bản chất cung này vốn {_short(cpos, 100)}.")
    if good_phu:
        g_names = _join_names(good_phu, 4)
        g_gen = "; ".join(_short(STAR_META.get(s["key"], {}).get("general", ""), 90)
                          for s in good_phu[:3] if STAR_META.get(s["key"], {}).get("general"))
        ban += f" Về phụ tinh, {g_names} {_cli('là điểm tựa, hỗ trợ', g_gen)}."
    if bad_phu:
        b_names = _join_names(bad_phu, 4)
        b_gen = "; ".join(_short(STAR_META.get(s["key"], {}).get("general", ""), 90)
                          for s in bad_phu[:3] if STAR_META.get(s["key"], {}).get("general"))
        ban += f" Đồng thời {b_names} {_cli('tạo sức ép hoặc rủi ro', b_gen)}."
    if neu_phu:
        n_names = _join_names(neu_phu, 4)
        ban += f" Một số sao trung tính như {n_names} khiến cung này nhạy hơn với hoàn cảnh và cách ứng xử."
    if rings:
        parts = [f"{g} ({', '.join(names)})" for g, names in rings.items()]
        ban += " Về bộ sao: " + ", ".join(parts) + " — cho biết mức thịnh/suy và vận thời trong cung."

    # ---- Điểm mạnh ----
    pos_parts = []
    for s in main[:2]:
        p = _short(s["obj"]["positive"], 100)
        if p:
            pos_parts.append(p)
    if not main:
        pos_parts.append(_short(cpos, 110))
    for s in good_phu[:3]:
        g = STAR_META.get(s["key"], {}).get("general", "")
        if g:
            pos_parts.append(f"{s['name']} {_short(g, 70)}")
    pos = (" ; ".join(pos_parts) if pos_parts
           else "Không có nhóm sao nổi bật để khẳng định; cần xét qua cách cục và bộ sao.")

    # ---- Điểm yếu / cẩn trọng ----
    neg_parts = []
    for s in main[:2]:
        n = _short(s["obj"]["negative"], 100)
        if n:
            neg_parts.append(n)
    if not main:
        neg_parts.append(_short(cneg, 110))
    for s in bad_phu[:3]:
        g = STAR_META.get(s["key"], {}).get("general", "")
        if g:
            neg_parts.append(f"{s['name']} {_short(g, 70)}")
    neg = (" ; ".join(neg_parts) if neg_parts
           else "Nhóm này không lộ điểm yếu cực đoan, nhưng vẫn phải cẩn thận vì thiếu sao đối trọng.")

    return {"ban": ban, "pos": pos, "neg": neg}


def _cli(kind: str, gen: str) -> str:
    """Nối cụm 'là điểm tựa, hỗ trợ' với nội dung ẩn nghĩa sao."""
    if not gen:
        return kind
    return f"{kind} ({gen})"


def build_cung_block(row, menh: int, cung_index: int):
    """Toàn bộ khối markdown cho một cung, có liệt kê sao + đoạn liên kết."""
    stars = cung_stars(row, menh, cung_index)
    if not stars:
        return []
    cung_name, domain, _, _, advice = CUNG_PROFILE[cung_index]
    main = _main_stars(stars)
    phu = _notable_phu(stars)
    rings = _rings(stars)

    lines = [f"### {cung_name} — {domain}"]
    if main:
        lines.append(f"- **Chính tinh:** {_join_names(main, 6)}")
    if phu:
        lines.append(f"- **Phụ tinh đáng chú ý:** {_join_names(phu, 8)}")
    for g, names in rings.items():
        lines.append(f"- **{g}:** {', '.join(names)}")
    lines.append("")
    synth = _synthesize_cung(stars, cung_index)
    lines.append(f"**Bản chất liên kết:** {synth['ban']}")
    lines.append("")
    lines.append(f"**Điểm mạnh:** {synth['pos']}")
    lines.append("")
    lines.append(f"**Điểm yếu / cần lưu ý:** {synth['neg']}")
    lines.append("")
    if advice:
        lines.append(f"**Gợi ý cho cung {cung_name}:** {advice}")
        lines.append("")
    return lines


def build_overview(row, menh: int, than: int):
    """Đoạn tổng quan liên kết: Mệnh/Thân + Tứ Hoá + các cung trọng yếu."""
    stars_m = cung_stars(row, menh, 0)
    than_cung = (than - menh) % 12
    stars_t = cung_stars(row, menh, than_cung)
    main_m = _main_stars(stars_m)
    main_t = _main_stars(stars_t)
    phu_m = _notable_phu(stars_m)
    phu_t = _notable_phu(stars_t)

    lines = []
    m_names = _join_names(main_m, 3) or "không có chính tinh"
    t_names = _join_names(main_t, 3) or "không có chính tinh"
    _cc = lambda ci: CUNG_PROFILE[ci][0]
    lines.append("**Đọc tổng quan:**")
    lines.append("")
    if than_cung == 0:
        lines.append(
            f"Mệnh tại {CHI_NAMES[menh]} (cung Mệnh), Thân tại {CHI_NAMES[than]} "
            "(cung Mệnh — Thân cư Mệnh: bản thân và việc làm gắn chặt, thành bại do tự mình quyết)."
        )
    else:
        lines.append(
            f"Mệnh tại {CHI_NAMES[menh]} (cung Mệnh), Thân tại {CHI_NAMES[than]} "
            f"(cung {_cc(than_cung)} — liên quan tới giai đoạn trưởng thành)."
        )
    lines.append("")
    lines.append(
        f"Chính tinh đóng ở Mệnh gồm: {m_names}. Nếu kể cả các phụ tinh "
        f"{_join_names(phu_m, 5)}, bản chất con người thiên về "
        f"{_short((main_m[0]['obj']['ban_chat'] if main_m else 'phụ tinh quyết định'), 150)}."
    )
    lines.append("")
    if than_cung != 0 and main_t:
        lines.append(
            f"Thân cung có chính tinh {t_names}: {_short(main_t[0]['obj']['ban_chat'], 150)}."
        )
    key_info = []
    for idx, label in ((4, "Quan Lộc"), (8, "Tài Bạch"), (10, "Phu Thê")):
        st = cung_stars(row, menh, idx)
        if not st:
            continue
        sy = _synthesize_cung(st, idx)
        mn = _join_names(_main_stars(st), 2) or "không chính tinh"
        key_info.append(f"{label} ({mn}): {_short(sy['pos'], 100)}")
    if key_info:
        lines.append("Trên các trục quan trọng: " + " ; ".join(key_info) + ".")
        lines.append("")
    return lines


def _cung_name(cung_index: int) -> str:
    return CUNG_PROFILE[cung_index][0]


def build_cung_analysis(row, menh: int, skip=()):
    """Toàn bộ 12 cung, mỗi cung một khối liên kết; `skip` là cung đã đọc trước."""
    skip = set(skip)
    lines = []
    for cung_index in range(12):
        if cung_index in skip:
            continue
        lines += build_cung_block(row, menh, cung_index)
    return lines
