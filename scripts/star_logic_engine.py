# -*- coding: utf-8 -*-
"""
star_logic_engine.py
====================
Hệ thống LOGIC LUẬN GIẢI SAO và TƯƠNG TÁC SAO.

Hai lớp logic:

1. `star_logic(star_key, cung_index)`
   - Luận một sao đơn lẻ (bản chất/tích cực/tiêu cực) + thẻ ngữ nghĩa (tags).

2. `pair_logic(star_a, star_b)`
   - Luận một cặp sao khi gặp nhau: loại tương tác, bản chất, tích cực,
     tiêu cực, lưu ý.
   - Tương tác được quyết định bởi:
        a) cặp nổi tiếng nếu có trong `INTERACTION_SPECIFIC`.
        b) quy tắc theo cặp thẻ ngữ nghĩa (tags).
        c) quy tắc dự phòng theo thiên tính (cát/hung).
   - `classify_interaction(a,b)` cho biết kết luận: "hợp thành", "tăng lực",
     "chế ngự / cần cân bằng", "cộng hung", "tán hao", "tuỳ ngữ cảnh".

Dùng trong engine luận giải để:
   - tạo `logic_for_chart()` gồm mọi sao trong chart và mọi cặp có quan hệ
     (cùng cung / tam hợp / xung chiếu) hoặc thuộc cặp nổi tiếng.
"""

from __future__ import annotations

from scripts.luan_giai_knowledge import CUNG_PROFILE, STAR_PROFILE
from scripts.luan_giai_objective import objective_for_star_cung
from scripts.star_knowledge_data import STAR_META

MAIN_KEYS = [
    "tu_vi", "thien_co", "thai_duong", "vu_khuc", "thien_dong", "liem_trinh",
    "thien_phu", "thai_am", "tham_lang", "cu_mon", "thien_tuong",
    "thien_luong", "that_sat", "pha_quan",
]

# Bộ sao tham gia "logic tương tác" (chính tinh + phụ tinh + tứ hoá + cố định + tuần không).
LOGIC_STARS = MAIN_KEYS + [
    "thien_quang", "thien_phuc", "luu_ha", "thien_tru", "quang_an_can",
    "kinh_duong", "da_la", "thien_khoi", "thien_viet", "long_tri",
    "phuong_cac", "giai_than", "thien_khoc", "thien_hu", "thien_duc",
    "nguyet_duc", "hong_loan", "thien_hy", "co_than", "qua_tu", "dao_hoa",
    "thien_ma", "kiep_sat", "hoa_cai", "pha_toai", "thien_khong", "ta_phu",
    "huu_bat", "thien_hinh", "thien_dieu", "thien_y", "thien_giai",
    "dia_giai", "van_xuong", "van_khuc", "thai_phu", "phong_cao",
    "dia_khong", "dia_kiep", "hoa_tinh", "linh_tinh", "tam_thai", "bat_toa",
    "an_quang", "thien_quy", "hoa_loc", "hoa_quyen", "hoa_khoa", "hoa_ky",
    "thien_la", "dia_vong", "thien_thuong", "thien_su", "dau_quan",
    "thien_tai", "thien_tho", "tuan", "triet_1", "triet_2",
]

# --------------------------------------------------------------------------- #
# Thẻ ngữ nghĩa của từng sao.
# --------------------------------------------------------------------------- #
STAR_TAGS = {
    # 14 chính tinh
    "tu_vi": {"quyen", "uy"},
    "thien_co": {"tri", "bien"},
    "thai_duong": {"quang", "tinh", "hanh"},
    "vu_khuc": {"tai", "hanh"},
    "thien_dong": {"phuc", "tinh", "an"},
    "liem_trinh": {"uy", "quyen", "cuong"},
    "thien_phu": {"tai", "an", "binh"},
    "thai_am": {"tinh", "phuc", "tri"},
    "tham_lang": {"tai", "tinh", "duc"},
    "cu_mon": {"tri", "khau", "tinh"},
    "thien_tuong": {"quyen", "binh", "an"},
    "thien_luong": {"phuc", "tri", "cuu"},
    "that_sat": {"hanh", "uy", "hung"},
    "pha_quan": {"hanh", "bien", "pha"},
    # phụ tinh
    "thien_quang": {"quang", "phuc", "quy_nhan"},
    "thien_phuc": {"phuc", "tai"},
    "luu_ha": {"bien", "phuc"},
    "thien_tru": {"tai", "an"},
    "quang_an_can": {"quyen", "tri", "van"},
    "kinh_duong": {"hanh", "hung", "uy"},
    "da_la": {"hanh", "hung", "bien"},
    "thien_khoi": {"tri", "quy_nhan", "van"},
    "thien_viet": {"quy_nhan", "van", "tri"},
    "long_tri": {"uy", "quyen", "van"},
    "phuong_cac": {"van", "quyen"},
    "giai_than": {"cuu", "phuc"},
    "thien_khoc": {"tinh", "tan"},
    "thien_hu": {"tan", "hung"},
    "thien_duc": {"phuc", "cuu"},
    "nguyet_duc": {"phuc", "tinh", "cuu"},
    "hong_loan": {"tinh", "dao_hoa"},
    "thien_hy": {"tinh", "phuc", "dao_hoa"},
    "co_than": {"co_don", "tinh"},
    "qua_tu": {"tan", "tinh"},
    "dao_hoa": {"tinh", "dao_hoa", "bien"},
    "thien_ma": {"bien", "hanh"},
    "kiep_sat": {"hung", "tan", "tai"},
    "hoa_cai": {"tri", "van", "co_don"},
    "pha_toai": {"tan", "hung", "tai"},
    "thien_khong": {"tan", "khong"},
    "ta_phu": {"quy_nhan", "phuc", "tri"},
    "huu_bat": {"quy_nhan", "phuc", "tai"},
    "thien_hinh": {"hung", "uy"},
    "thien_dieu": {"tinh", "tai", "bien"},
    "thien_y": {"phuc", "cuu"},
    "thien_giai": {"cuu", "phuc"},
    "dia_giai": {"cuu", "phuc"},
    "van_xuong": {"tri", "van"},
    "van_khuc": {"tri", "van", "tai"},
    "thai_phu": {"phuc", "quy_nhan", "tai"},
    "phong_cao": {"bien", "van", "quyen"},
    "dia_khong": {"tan", "khong", "hung"},
    "dia_kiep": {"tan", "hung", "tai"},
    "hoa_tinh": {"hanh", "hung"},
    "linh_tinh": {"tri", "hung", "bien"},
    "tam_thai": {"phuc", "quy_nhan"},
    "bat_toa": {"quyen", "an"},
    "an_quang": {"quang", "phuc", "quy_nhan"},
    "thien_quy": {"quy_nhan", "phuc", "quyen"},
    # tứ hoá
    "hoa_loc": {"tai", "phuc", "hoa"},
    "hoa_quyen": {"quyen", "hanh", "hoa"},
    "hoa_khoa": {"tri", "van", "quy_nhan", "hoa"},
    "hoa_ky": {"tan", "hung", "hoa"},
    # sao cố định
    "thien_la": {"hung", "bien"},
    "dia_vong": {"hung", "bien"},
    "thien_thuong": {"hung", "tan"},
    "thien_su": {"bien", "tan"},
    "dau_quan": {"quyen", "uy", "tri"},
    "thien_tai": {"tai", "tri"},
    "thien_tho": {"phuc", "an"},
    # tuần không
    "tuan": {"tan", "hung"},
    "triet_1": {"tan", "khong"},
    "triet_2": {"tan", "khong"},
}


def _name(key):
    meta = STAR_META.get(key, {})
    if meta.get("name"):
        return meta["name"]
    return STAR_PROFILE.get(key, {}).get("name", key)


def _nature(key):
    return STAR_META.get(key, {}).get("nature", "trung")


def star_tags(key):
    return STAR_TAGS.get(key, set())


# --------------------------------------------------------------------------- #
# Logic một sao đơn lẻ.
# --------------------------------------------------------------------------- #
def _single_for(key, cung_index):
    name = _name(key)
    meta = STAR_META.get(key, {})
    nature = meta.get("nature", "trung")
    general = meta.get("general", "")
    group = meta.get("group", "")
    tags = sorted(star_tags(key))

    if key in MAIN_KEYS and cung_index is not None:
        obj = objective_for_star_cung(key, cung_index)
        ban = obj["ban_chat"]
        positive = obj["positive"]
        negative = obj["negative"]
    else:
        if general:
            ban = f"{name}: {general}"
        else:
            ban = f"{name}: sao có tính chất riêng trong nhóm {group or 'phu tinh'}."
        positive = _single_positive(nature, name)
        negative = _single_negative(nature, name)

    return {
        "star": key,
        "name": name,
        "group": group,
        "nature": nature,
        "tags": tags,
        "ban_chat": ban,
        "positive": positive,
        "negative": negative,
    }


def _single_positive(nature, name):
    if nature in ("tốt", "cát"):
        return (f"{name} là sao tốt: nếu được đắc vị và hội sao hỗ trợ, phát huy mặt "
                f"tích cực của nó; nên biết tận dụng đúng cung.")
    if nature in ("xấu", "xấu-trung"):
        return (f"{name} mang tính cản trở/phiền phức nhưng không phải tuyệt đối: nếu "
                f"được tiết chế và chọn đúng cung, có thể chuyển thành nghị lực, cảnh giác.")
    return f"{name} là sao trung tính: tạo tính cách hai chiều, phụ thuộc cách vận dụng."


def _single_negative(nature, name):
    if nature in ("xấu", "xấu-trung"):
        return (f"{name} là điểm yếu cần nhìn thẳng: dễ gây thị phi, tổn thất, nóng vội "
                f"hoặc lo lắng nếu không kiểm soát.")
    if nature in ("tốt", "cát"):
        return (f"{name} khi quá mạnh cũng thành bất lợi: dễ tự mãn, ỷ lại, mất cảnh giác, "
                f"thiếu thực tế.")
    return f"{name} dễ làm tính cách không ổn định, lưỡng lự hoặc phụ thuộc hoàn cảnh."


def star_logic(key, cung_index=None):
    return _single_for(key, cung_index)


# --------------------------------------------------------------------------- #
# Logic TƯƠNG TÁC giữa hai sao.
# --------------------------------------------------------------------------- #
# Cặp nổi tiếng, ghi đè rule chung.
INTERACTION_SPECIFIC = {
    ("tu_vi", "thien_phu"): ("quyền-tài", "hợp thành",
        "Tử Vi (quyền) và Thiên Phủ (tài) tạo 'đế vương có kho': quyền lực đi cùng của cải.",
        "Được quý nhân, quyền hành, tài sản; lãnh đạo bền vững, làm việc lớn.",
        "Tự đắc, gia trưởng; dễ bị tiểu nhân bao vây; quá coi trọng địa vị.",
        "Rất mạnh ở Mệnh/Quan/Điền; gặp hung tinh dễ thành 'vua không ngai'."),
    ("thien_phu", "thien_tuong"): ("an định", "tăng lực",
        "Phủ (kho) + Tướng (bảo hộ): một bộ sao ổn định, có cơ nghiệp.",
        "Ổn định, biết tổ chức, được người giúp đỡ, hợp quản lý tài chính.",
        "Thụ động, thích an toàn, thiếu quyết đoán khi cần đổi mới.",
        "Rất hợp Điền/Quan/Tài."),
    ("vu_khuc", "tham_lang"): ("tài-dục", "hợp thành",
        "Vũ Khúc (kỷ luật tài chính) + Tham Lang (dục/tài) tạo 'Vũ Tham': tham vọng tiền quyền.",
        "Nhanh nhạy, biết kiếm tiền, giỏi đầu tư, thành công ở kinh doanh.",
        "Ham hố dẫn tới tham lam, thủ đoạn; giàu nhanh bại cũng nhanh.",
        "Đắc địa ở Thìn/Tuất/Sửu/Mùi mạnh; có Hỏa/Linh tăng nghị lực."),
    ("tu_vi", "tham_lang"): ("quyền-tham", "hợp thành",
        "Tử Vi + Tham Lang 'Tử Tham': đế vương có tham vọng lớn.",
        "Bản lĩnh, có lãnh đạo, làm lớn, có thể phát tài phi thường.",
        "Quyền lực dễ thành quyền tham; tham quá mất uy, dễ bị phản.",
        "Cần tài đức và người góp ý; gặp cát tinh mới thành quý."),
    ("tu_vi", "that_sat"): ("quyền-quyết", "tăng lực",
        "Tử Vi + Thất Sát 'Tử Sát': quyền uy đi cùng quyết đoán, khí phách chỉ huy.",
        "Mạnh mẽ, dám quyết, có sức chỉ huy, làm lớn trong môi trường kỷ luật.",
        "Cứng nhắc, độc đoán, dễ xung đột; quyền lực dễ bị lạm dụng.",
        "Rất hợp Quan/Điền; gặp hung tinh dễ thành bạo tàn."),
    ("tu_vi", "pha_quan"): ("bứt phá", "xung kích",
        "Tử Vi + Phá Quân 'Tử Phá': quyền lực gặp phá cựu lập tân.",
        "Tầm nhìn lớn, dám thay đổi, tạo bước ngoặt lớn.",
        "Phá nhiều hơn xây; rủi ro cao, dễ mất ổn định.",
        "Cần sự sẵn sàng về tài chính và thời cơ."),
    ("thai_duong", "thai_am"): ("âm-dương", "cân bằng",
        "Nhật Nguyệt đối xứng: cân bằng sáng/âm, tự tin và tình cảm.",
        "Khôn ngoan, hài hoà, có phúc, giỏi giao tiếp và thấu cảm.",
        "Hay do dự, tính hai chiều, dễ mệt mỏi vì cân bằng thái quá.",
        "Đắc địa rất tốt; hãm địa dễ bi quan."),
    ("thien_co", "thien_luong"): ("trí-phúc", "hợp thành",
        "Cơ Lương: tư duy cùng phước, cứu giải.",
        "Thông minh, có phước, dễ được cứu giúp; hợp phân tích, tư vấn.",
        "Lo xa, băn khoăn; thương người quá mà mệt mình.",
        "Càng đắc càng tốt."),
    ("thien_dong", "thai_am"): ("an-nhàn", "tăng lực",
        "Đồng Âm: hiền hoà và trăng thanh, sống tình cảm.",
        "Dễ chịu, có phúc, được yêu mến; hợp nghệ thuật, chăm sóc.",
        "Mềm yếu, hay buồn, thiếu tham vọng; dễ bị tình cảm chi phối.",
        "Đắc địa rất tốt."),
    ("thien_dong", "cu_mon"): ("khẩu-tài", "cân bằng",
        "Đồng Cự: hoà nhã gặp khẩu tài phản biện.",
        "Khéo giao tiếp, học nhanh, giỏi giảng dạy, tranh luận.",
        "Thích biện luận, hay cãi vặt; tính tình thay đổi.",
        "Hãm địa dễ 'miệng quạ'; cần cẩn ngôn."),
    ("thien_luong", "cu_mon"): ("luận-thuyết", "hợp thành",
        "Lương Cự: phước gặp miệng, trí tuệ và hoạ giải.",
        "Thông minh, dạy đời, nói có sức thuyết phục, hay hoá giải thị phi.",
        "Hay diễn giải, khinh người; tự cho mình đúng, dễ mất lòng.",
        "Ở Mệnh/Thân phát huy rất tốt."),
    ("thai_duong", "cu_mon"): ("nhật-cự", "cân bằng",
        "Nhật Cự: ánh sáng và bóng tối, sáng suốt nhưng đa nghi.",
        "Giỏi phát hiện vấn đề; hợp điều tra, luật, báo.",
        "Đa nghi, soi mói, dễ thị phi; cái sáng có thể thành quá đà.",
        "Đắc địa phát huy mạnh."),
    ("thai_am", "cu_mon"): ("ẩn-miệng", "cân bằng",
        "Âm Cự: sâu kín gặp miệng lưỡi, nhạy cảm và phản biện.",
        "Sâu sắc, trí nhớ tốt; hợp nghiên cứu, tâm lý.",
        "Hay bực bội, khó tính, giận dỗi; miệng lưỡi dễ đâm chọc.",
        "Hãm địa rất xấu; cần kiềm chế cảm xúc."),
    ("thai_duong", "that_sat"): ("nhiệt-quyết", "tăng lực",
        "Nhật Sát: nhiệt huyết và quyết liệt.",
        "Mạnh mẽ, quyết đoán, sức nổ lực lớn; hợp kinh doanh, quân đội.",
        "Nóng nảy, dễ xung đột, bị hiểu lầm.",
        "Đắc địa có uy; hãm địa dễ thành hung hiểm."),
    ("thai_duong", "thien_luong"): ("phúc-hiệp", "tăng lực",
        "Nhật Lương: sáng suốt và phước đức, hay giúp đời.",
        "Tốt bụng, hào hiệp, có uy tín; hợp y, giáo, từ thiện.",
        "Ôm việc quá, mềm yếu, dễ bị lợi dụng lòng tốt.",
        "Gặp cát tinh rất tốt."),
    ("thai_am", "thien_luong"): ("tĩnh-phúc", "tăng lực",
        "Âm Lương: nội tâm và phước, sống nhẹ nhàng.",
        "Hiền, có đức, vận may; thích cái đẹp và tâm linh.",
        "Thụ động, hay buồn, lo xa, thiếu quyết đoán.",
        "Đắc địa sống an yên."),
    ("liem_trinh", "that_sat"): ("kim-khí", "tăng lực",
        "Liêm Sát: sự cứng và mạnh, đồng cung hoặc tam hợp.",
        "Có khí phách, dám đối đầu; làm nghề quân, pháp, công an.",
        "Cực đoan, hung hãn; dễ tự hại và gây nạn.",
        "Rất cần cát tinh."),
    ("liem_trinh", "pha_quan"): ("quyết-liệt", "xung kích",
        "Liêm Phá: sự cứng rắn và phá phách.",
        "Mạnh, dám đổi mới; quyết liệt trong nghề.",
        "Phá hoại, thất thường, dễ làm mất thể diện.",
        "Cần sự tự chủ rất cao."),
    ("loc_ton", "tu_vi"): ("phú-quý", "tăng lực",
        "Lộc Tồn đi cùng Tử Vi: tài lộc gặp uy quyền, 'vua có kho'.",
        "Có tiền, có quyền, có phước; sống dư dả và được quý.",
        "Càng giàu càng dễ kiêu, bị nịnh và ganh.",
        "Đắc địa rất tốt."),
    ("loc_ton", "thien_phu"): ("đại-phú", "tăng lực",
        "Lộc Tồn + Thiên Phủ: lộc đi cùng kho tàng — cực thuận tài.",
        "Dồi dào tài sản, biết giữ của; sống sung túc.",
        "Có thể trở nên keo kiệt, nặng vật chất.",
        "Rất tốt ở Tài/Điền."),
    ("loc_ton", "tham_lang"): ("phú-tham", "cân bằng",
        "Lộc Tồn + Tham Lang: lộc gặp dục — tiền nhiều nhưng ham.",
        "Biết kiếm tiền, có cơ hội phát tài lớn.",
        "Tham lam, tiêu hoang; càng lộc càng dễ sa đà.",
        "Cần kiểm soát ham muốn."),
    ("kinh_duong", "tu_vi"): ("quyền-xung", "chế ngự",
        "Kình Dương đi cùng Tử Vi: gai nhọn bên cạnh vua — quyền uy có lực cản.",
        "Bản lĩnh, cương trực, dám chống sai.",
        "Khó gần, hay tranh chấp, dễ mất lòng, gây hiềm khích.",
        "Tử Vi vẫn giữ quyền nhưng phải đối đầu trắc trở."),
    ("da_la", "tu_vi"): ("quyền-trệ", "chế ngự",
        "Đà La đi cùng Tử Vi: sự trì trệ bên vua — quyền nhưng chậm.",
        "Kiên trì, không nản, có chính kiến.",
        "Hay bị cản trở, nợ nần, khó khăn kéo dài.",
        "Phải nhẫn nại và tránh quyết định vội."),
    ("hoa_tinh", "tham_lang"): ("hoả-tham", "tăng lực",
        "Hỏa Tham: lửa đốt lòng tham, nghị lực bốc cao.",
        "Đắc địa: nhiệt huyết, ham làm ăn, thành công lớn.",
        "Hãm địa: nóng, thô, dễ mất bình tĩnh, gây rủi ro.",
        "Mạnh ở Mệnh/Quan; phải có lý trí."),
    ("linh_tinh", "tham_lang"): ("linh-tham", "tăng lực",
        "Linh Tham: ma thuật, sắc sảo.",
        "Thông minh, có duyên nghệ thuật, quyết đoán.",
        "Ám muội, đa nghi, dễ lợi dụng thủ đoạn.",
        "Đắc địa thành tài; hãm thành hung."),
    ("van_xuong", "van_khuc"): ("văn-học", "hợp thành",
        "Xương Khúc: học vấn, văn chương.",
        "Thông minh, học giỏi, có tài văn chương; công danh tốt.",
        "Dễ tài hoa mà phận, hay lo xa; gặp Hóa Kỵ dễ rối trí.",
        "Ở Mệnh/Quan/Tài rất thuận."),
    ("thien_khoi", "thien_viet"): ("quý-nhân", "hợp thành",
        "Khôi Việt: bộ quý nhân, đỡ vấp ngã.",
        "Gặp quý nhân, học hành, công danh thuận; tai qua nạn khỏi.",
        "Phụ thuộc người khác; dễ được giúp mà thiếu tự lực.",
        "Ở Mệnh/Quan rất tốt."),
    ("dao_hoa", "hong_loan"): ("đào-hoa", "tăng lực",
        "Đào Loan: tình duyên rực rỡ.",
        "Sức hút, duyên tình thuận, hợp kết hôn, nghề liên quan cái đẹp.",
        "Đào hoa quá mạnh: dễ ngoại tình, thị phi, hao tiền vì tình.",
        "Ở Phu Thê vừa tốt vừa cần kiềm chế."),
    ("dao_hoa", "thien_ma"): ("phiêu-du", "cân bằng",
        "Đào Hoa + Thiên Mã: tình duyên và di chuyển — tình đi xa.",
        "Duyên tình mới, thú vị; gặp người ở nơi khác.",
        "Tình cảm không ổn, đi lại vất vả, dễ bỏ lỡ.",
        "Cần cân bằng tình và việc."),
    ("hoa_loc", "tu_vi"): ("đế-lộc", "tăng lực",
        "Hóa Lộc tọa Tử Vi: quyền được thêm lộc, 'vua được kho'.",
        "Tiền và quyền song hành, thành công lớn.",
        "Càng nhiều quyền lộc càng dễ mất phương hướng nếu không có đức.",
        "Rất tốt ở Mệnh/Quan."),
    ("hoa_ky", "tu_vi"): ("đế-kỵ", "chế ngự",
        "Hóa Kỵ tọa Tử Vi: quyền bị vướng bận, thành nhưng vất vả.",
        "Có quyền thật nhưng nhọc công; biết vượt khó sẽ được.",
        "Lo âu, gánh nặng, dễ mất của vì lụy quyền.",
        "Hóa Kỵ làm đế tinh giảm sức."),
    ("hoa_ky", "thai_am"): ("âm-kỵ", "chế ngự",
        "Hóa Kỵ tọa Thái Âm: tình cảm và tài lộc có vướng.",
        "Trân trọng cảm xúc, biết lo xa.",
        "Lo buồn, hao tài, dễ bi quan.",
        "Cần học cách buông bỏ."),
    ("cu_mon", "that_sat"): ("khẩu-xung", "cân bằng",
        "Cự Môn + Thất Sát: miệng sắc gặp tay mạnh.",
        "Sắc sảo, quyết đoán khi làm đúng.",
        "Nói và làm đều nóng; dễ bệnh miệng, thị phi, xung đột.",
        "Cần rèn kiềm chế."),
    ("cu_mon", "kinh_duong"): ("thị-phi", "chế ngự",
        "Cự Môn + Kình Dương: lưỡi dao cạnh miệng.",
        "Đấu tranh, phản biện mạnh mẽ.",
        "Hay cãi cọ, tự hại, kết oán.",
        "Rất cần cẩn ngôn."),
    ("cu_mon", "da_la"): ("cản-trở", "chế ngự",
        "Cự Môn + Đà La: miệng và sự rào cản.",
        "Dai dẳng, có sức chịu đựng.",
        "Tranh chấp kéo dài, nợ miệng.",
        "Cần tránh dây dưa."),
    ("that_sat", "pha_quan"): ("phá-hại", "xung kích",
        "Sát Phá: mạnh và phá, đầy nhiệt.",
        "Làm lớn, dám thay đổi, táo bạo.",
        "Bạo, dễ nổ, phá tiền và phá quan hệ.",
        "Phải có kỷ luật thép."),
    ("that_sat", "thien_tuong"): ("oai-phong", "tăng lực",
        "Sát Tướng: mạnh có chỉ huy.",
        "Có khả năng lãnh đạo kỷ luật, quân đội, công an.",
        "Thiếu mềm mỏng, cương quá.",
        "Kết hợp tốt ở Quan/Điền."),
    ("pha_quan", "thien_tuong"): ("đổi-tướng", "cân bằng",
        "Phá Tướng: đổi mới có người bảo.",
        "Bứt phá nhưng có nền tảng, dễ phát triển.",
        "Thất thường, hay thay đổi kế hoạch.",
        "Cần người cố vấn ổn định."),
    ("liem_trinh", "thien_phu"): ("liêm-phủ", "hợp thành",
        "Liêm Phủ: cương có nơi chứa.",
        "Có chức quyền và tài sản, biết dữ.",
        "Cương quá dễ khó nghe; của nhiều dễ thành ách.",
        "Đắc địa rất tốt ở Tài/Quan."),
    ("liem_trinh", "thien_tuong"): ("liêm-tướng", "hợp thành",
        "Liêm Tướng: hàm hạnh, văn võ.",
        "Có sức thuyết phục, kỷ luật tốt.",
        "Khó tính, kén người.",
        "Kết hợp rất tốt ở Mệnh/Quan."),
    ("tu_vi", "thien_tuong"): ("quyền-tướng", "hợp thành",
        "Tử Vi + Thiên Tướng 'Tử Tướng': vua gặp tướng, quyền có người phò.",
        "Có quyền mà biết lãnh đạo, được người giúp, uy tín vững.",
        "Dễ ỷ vào cấp dưới; quyền bị giữ hộ nên có thể thiếu trực tiếp.",
        "Rất hợp Mệnh/Quan/Điền; cần tự quyết những việc lớn."),
    ("thien_dong", "thien_luong"): ("đồng-lương", "hợp thành",
        "Đồng Lương: hiền lành gặp phước đức, một bộ sao phúc và thông minh.",
        "Sống nhân hậu, dễ gặp quý nhân, học hỏi tốt, cuộc sống dễ an.",
        "Hiền quá dễ bị lợi dụng, thiếu tham vọng, khó quyết lớn.",
        "Đắc địa ở Mệnh/Phúc rất tốt."),
    ("vu_khuc", "thien_phu"): ("vũ-phủ", "hợp thành",
        "Vũ Phủ: kỷ luật tài chính gặp kho tàng, làm ra của và giữ của.",
        "Biết kiếm tiền, quản lý tốt, có nền tảng tài chính vững.",
        "Nặng vật chất, keo kiệt; có của dễ sinh lo xa quá.",
        "Rất hợp Tài/Điền; gặp Hóa Lộc càng mạnh."),
    ("tu_vi", "thien_co"): ("tử-cơ", "hợp thành",
        "Tử Cơ: quyền lực đi cùng mưu lược, vua có quân sư.",
        "Có tầm nhìn, biết dùng người, làm việc có kế hoạch.",
        "Mưu nhiều tâm lý nhiều; quyền dễ bị trí tuệ phản tác dụng nếu gian xảo.",
        "Hợp Mệnh/Quan; nên minh bạch trong toan tính."),
    ("tu_vi", "thai_duong"): ("tử-dương", "tăng lực",
        "Tử Dương: đế tinh gặp mặt trời, quyền uy thêm hào quang.",
        "Có uy, hào phóng, dễ thành danh, được nhiều người chú ý.",
        "Quá nổi bật dễ sinh kiêu, bị ganh, phô trương.",
        "Phải giữ lòng khiêm và sự thực tế."),
}

# Quy tắc tương tác theo cặp thẻ (fallback cho cặp chưa viết tay).
TAG_INTERACTION_RULES = {
    frozenset({"quyen", "tai"}): ("quyền-tài", "hợp thành",
        "{a} và {b}: quyền lực mở đường cho của cải, của cải nuôi quyền lực.",
        "Tạo đà thăng tiến, làm ăn lớn, được người ủng hộ.",
        "Dễ thành tham vọng quyền–lợi; quá đà dễ mất cân bằng đạo đức.",
        "Nên minh bạch và biết dừng."),
    frozenset({"quyen", "tri"}): ("quyền-trí", "hợp thành",
        "{a} và {b}: quyền có bạn đồng mưu, trí có chỗ phát huy.",
        "Quyết đoán có tính toán, dễ thành công trong quản lý, tư vấn, chính trị.",
        "Dễ thao túng, lý luận biến thành lý sự.",
        "Cần giữ phẩm chất và lắng nghe."),
    frozenset({"tai", "tri"}): ("tài-trí", "hợp thành",
        "{a} và {b}: biết kiếm tiền bằng đầu óc.",
        "Đầu tư thông minh, kinh doanh có chiến lược, học–kiếm tiền song hành.",
        "Tính toán quá kỹ dễ mất cơ hội; cũng dễ dùng mẹo, toan tính.",
        "Rất hợp khởi nghiệp bằng chuyên môn."),
    frozenset({"tai", "tinh"}): ("tài-tình", "cân bằng",
        "{a} và {b}: tiền và tình va chạm với nhau.",
        "Có khả năng lo toan vật chất cho người thân, hôn nhân có nền tảng.",
        "Dễ dùng tiền đổi tình, hao tổn vì cảm xúc; tình/tiền lệ thuộc nhau.",
        "Không để quà cáp thay thế sự chân thành."),
    frozenset({"quyen", "quyen"}): ("quyền-quyền", "tranh mạnh",
        "{a} và {b}: hai năng lượng quyền lực gặp nhau.",
        "Nếu biết phối hợp tạo liên minh mạnh, dễ cầm đầu.",
        "Ganh quyền, cấu kết, đấu đá; mạnh quá thiếu người đối trọng.",
        "Cần phân công rõ ràng."),
    frozenset({"tai", "tai"}): ("tài-tài", "tăng lực",
        "{a} và {b}: hai sao cùng thiên về tài lộc — của cải cộng hưởng.",
        "Có cơ hội tích luỹ tốt, đầu tư sinh lời.",
        "Dễ nặng vật chất, keo kiệt, tham lợi.",
        "Nên kèm người biết tiêu cho đúng."),
    frozenset({"tai", "hanh"}): ("tài-hành", "hợp thành",
        "{a} và {b}: tài năng đi cùng hành động.",
        "Làm ra tiền và dám hành động; kinh doanh, thực chiến tốt.",
        "Vì tiền mà liều, nóng vội; mất của khi mất bình tĩnh.",
        "Cần kế hoạch trước khi xung trận."),
    frozenset({"tinh", "hanh"}): ("tình-hành", "mâu thuẫn",
        "{a} và {b}: cảm xúc và hành động kéo ngược nhau.",
        "Nếu cân bằng sẽ vừa thấu cảm vừa quyết đoán.",
        "Dễ nóng giận vì cảm xúc, hành động thiếu suy nghĩ, hoặc ngược lại ủy mị.",
        "Cần tạm dừng trước khi quyết định lớn."),
    frozenset({"tri", "tri"}): ("trí-trí", "tăng lực",
        "{a} và {b}: hai sao cùng mạnh về tư duy — càng nghĩ càng sâu.",
        "Học giỏi, phân tích tốt, nghiên cứu, giải quyết vấn đề giỏi.",
        "Nghĩ nhiều mà không hành; càng thông minh càng dễ lo xa, nghi ngờ.",
        "Cần hành động để căn chỉnh suy nghĩ."),
    frozenset({"tri", "hanh"}): ("trí-hành", "hợp thành",
        "{a} và {b}: một bên thiên về tư duy, một bên thiên về hành động.",
        "Làm việc hiệu quả, dễ thành công khi kết hợp kế hoạch và nghị lực.",
        "Nếu lệch sẽ hoặc mơ mộng hoặc liều lĩnh.",
        "Chọn một việc rồi làm tới."),
    frozenset({"tinh", "dao_hoa"}): ("tình-duyên", "tăng lực",
        "{a} và {b}: tình cảm gặp đào hoa — sức hút, lãng mạn.",
        "Duyên tình thuận, dễ gây cảm tình, thích nghệ thuật.",
        "Đa tình, dễ vướng thị phi tình ái; thiếu điểm dừng.",
        "Phân định rõ chung–riêng."),
    frozenset({"tinh", "an"}): ("tình-ổn", "tăng lực",
        "{a} và {b}: tình cảm gặp ổn định — hiền hoà và bền.",
        "Đời sống tình cảm ấm, khó tính nhưng đáng tin.",
        "Dễ thụ động, ngại thay đổi, thiếu tham vọng.",
        "Thỉnh thoảng cần bước ra vùng an toàn."),
    frozenset({"phuc", "phuc"}): ("phúc-phúc", "tăng lực",
        "{a} và {b}: hai sao phúc đức — may mắn cộng hưởng.",
        "Có phước, dễ gặp lành; tai qua nạn khỏi; được quý nhân.",
        "Phước mà không rèn sẽ thành dựa dẫm, lười biếng.",
        "Làm thiện giữ phước."),
    frozenset({"phuc", "quy_nhan"}): ("phúc-quý", "tăng lực",
        "{a} và {b}: phước gặp quý nhân — một đời dễ được che chở.",
        "Gặp quý nhân, cơ hội tốt, cứu giải kịp thời.",
        "Phụ thuộc người khác, thiếu tự lập.",
        "Nên chủ động thay vì trông chờ."),
    frozenset({"phuc", "cuu"}): ("phúc-giải", "tăng lực",
        "{a} và {b}: phước gặp giải trừ — hoá giải rủi ro.",
        "Bệnh dễ khỏi, tranh chấp dễ lắng, đi xa có phước.",
        "Chủ quan, coi thường vì nghĩ luôn có người cứu.",
        "Khám định kỳ dù đang thấy khoẻ."),
    frozenset({"phuc", "tan"}): ("phúc-tán", "xung khắc",
        "{a} và {b}: phước gặp hao tán — phước bị hao bớt.",
        "Ít ra biết phòng xa, không dám liều cũng đỡ tổn thất.",
        "Tài lộc, phúc khí dễ hao hụt; chuyện tốt không bền.",
        "Giữ tiền, giữ sức, đừng lơ là."),
    frozenset({"hung", "hung"}): ("hung-hung", "cộng hung",
        "{a} và {b}: hai sao hung gặp nhau — năng lượng xấu cộng dồn.",
        "Nếu tỉnh, biến thành cảnh giác và nghị lực phòng thủ.",
        "Rủi ro kép: thị phi, tai nạn, tổn thất, xung đột rất dễ xảy ra.",
        "Cần tiết chế mạnh và kế hoạch phòng ngừa."),
    frozenset({"hung", "phuc"}): ("hung-phúc", "cần cân bằng",
        "{a} và {b}: hung gặp phúc — hung bị chế bớt nhưng vẫn còn.",
        "Có phước đỡ nên rủi ro không đến mức tận cùng.",
        "Không xem thường: vẫn có nguy cơ nếu chủ quan.",
        "Có sao phúc vẫn phải cẩn thận."),
    frozenset({"hung", "cuu"}): ("hung-giải", "cần cân bằng",
        "{a} và {b}: hung gặp giải trừ — rủi ro được hoá giải một phần.",
        "Gặp nạn có người giúp; bệnh tật, tai nạn nhẹ hơn.",
        "Hoá giải không phải xoá bỏ: vẫn cần phòng.",
        "Đừng coi việc phòng ngừa là thừa."),
    frozenset({"tan", "tan"}): ("tan-tan", "cộng tan",
        "{a} và {b}: hai sao hao tán/hư không — tài, sức, phước dễ bào mòn.",
        "Biết mình dễ mất nên biết tiết chế.",
        "Rất dễ hao tài, biến động, thành công sớm bại.",
        "Giữ vốn, giữ sức, giữ mối quan hệ lành."),
    frozenset({"tan", "cuu"}): ("tan-giải", "cần cân bằng",
        "{a} và {b}: hao tán gặp giải trừ — tổn hao có người đỡ.",
        "Biến cố nhẹ, tai qua nạn khỏi, vẫn giữ được phần nào.",
        "Không nên kỳ vọng mọi thứ tự lành.",
        "Chủ động vá lại chỗ hở."),
    frozenset({"bien", "bien"}): ("biến-biến", "cân bằng",
        "{a} và {b}: hai sao thay đổi/di động — đời sống nhiều chuyển biến.",
        "Thích nghi nhanh, đi xa có cơ hội, không ngại đổi mới.",
        "Khó ổn định, thay đổi liên tục, dễ bỏ dở.",
        "Chọn một hướng rồi bám."),
    frozenset({"van", "tri"}): ("văn-trí", "hợp thành",
        "{a} và {b}: văn chương gặp trí tuệ — học vấn cộng hưởng.",
        "Học hành, thi cử, sáng tác, nghiên cứu đều thuận.",
        "Hay chê người, hình thức hoá tri thức.",
        "Đem tri thức phục vụ thực tế."),
    frozenset({"quy_nhan", "quy_nhan"}): ("quý-nhân-kép", "tăng lực",
        "{a} và {b}: hai sao quý nhân — được giúp đỡ rất mạnh.",
        "Nhiều cửa ngã rẽ cũng có người giúp.",
        "Ỷ lại, thiếu tự lực; ai nâng mình không ai đỡ mình dậy?",
        "Học cách tự đứng dậy."),
    frozenset({"dao_hoa", "dao_hoa"}): ("đào-hoa-kép", "tăng lực",
        "{a} và {b}: hai sao đào hoa — sức hút thuộc dạng mạnh.",
        "Rất có duyên, dễ gây thiện cảm, hợp nghề ngoại giao, nghệ thuật.",
        "Đào hoa quá mạnh: thị phi tình ái, lợi dụng, khó chung thuỷ.",
        "Đặt ranh giới rõ ràng."),
    frozenset({"co_don", "co_don"}): ("cô-đơn-kép", "cân bằng",
        "{a} và {b}: hai sao cô đơn — sống nội tâm, ít chia sẻ.",
        "Sâu sắc, độc lập, không vội tin người.",
        "Cô độc, khó gần, dễ xa cách người thân.",
        "Chủ động kết nối."),
    frozenset({"quyen", "phuc"}): ("quyền-phúc", "hợp thành",
        "{a} và {b}: quyền gặp phúc — quyền lực có nền đức.",
        "Lãnh đạo có phước, làm lớn mà được ủng hộ.",
        "Lợi dụng quyền để hưởng phước, dễ bị mua chuộc.",
        "Quyền phải đi đôi với trách nhiệm."),
    frozenset({"quyen", "tan"}): ("quyền-tán", "cần cân bằng",
        "{a} và {b}: quyền gặp hao tán — quyền khó bền, dễ mất vị thế.",
        "Biết cách giữ thể diện và phòng thủ.",
        "Mất chức/quyền, hao danh, công sức dễ đổ sông.",
        "Tránh phô trương quyền lực."),
    frozenset({"hanh", "hung"}): ("hành-hung", "cộng hung",
        "{a} và {b}: hành động gặp hung — nhanh và nguy hiểm.",
        "Nếu có kỷ luật, thành tốc độ và bản lĩnh.",
        "Nóng, liều, dễ chấn thương, tai nạn, tranh đấu.",
        "Cần phanh gấp trước khi quyết."),
    frozenset({"tai", "hung"}): ("tài-hung", "cần cân bằng",
        "{a} và {b}: tài gặp hung — tiền và rủi ro đi cùng.",
        "Có cơ hội lời nhanh, làm ăn mạo hiểm.",
        "Mất của, rủi ro nợ nần, tranh chấp.",
        "Chỉ đặt cược số tiền chấp nhận mất."),
    frozenset({"tinh", "tan"}): ("tình-tán", "cần cân bằng",
        "{a} và {b}: tình gặp hao tán — tình cảm dễ tổn thất.",
        "Nhạy cảm, thấu hiểu, biết trân trọng.",
        "Dễ buồn, hụt hẫng, mệt vì tình.",
        "Đừng để cảm xúc quyết định tài chính."),
}

NATURE_RULES = {
    ("cát", "cát"): ("cát-cát", "tăng lực",
        "{a} (tốt) gặp {b} (tốt): hai sao tốt cộng hưởng.",
        "Dễ được giúp đỡ, ổn định, phát triển theo hướng tích cực.",
        "Càng mạnh càng dễ tự mãn, mất cảnh giác.",
        "Đánh giá theo đắc/hãm và cung đóng."),
    ("xấu", "xấu"): ("hung-hung", "cộng hung",
        "{a} (xấu) gặp {b} (xấu): rủi ro cộng dồn.",
        "Biết rõ rủi ro để phòng; nghị lực rèn từ khó khăn.",
        "Dễ tổn thất, thị phi, tai nạn, căng thẳng.",
        "Phải chủ động phòng ngừa."),
    ("cát", "xấu"): ("tốt-xấu", "cần cân bằng",
        "{a} (tốt) gặp {b} (xấu): tốt giữ nền, xấu tạo trở ngại.",
        "Có nền tốt nên khó khăn không phải tất cả.",
        "Ảnh hưởng xấu vẫn có thật; dễ bị kéo lệch.",
        "Cần tỉnh và chuẩn bị."),
    ("xấu", "cát"): ("tốt-xấu", "cần cân bằng",
        "{a} (xấu) gặp {b} (tốt): tốt giảm bớt rủi ro.",
        "Có chỗ dựa, dễ được cứu vãn.",
        "Rủi ro vẫn còn; không được lơ là.",
        "Khai thác cứu tinh, đồng thời phòng thủ."),
}


def _tags_of(key):
    return STAR_TAGS.get(key, set())


def classify_interaction(a: str, b: str):
    """Trả về (loại, kiểu tương tác) cho cặp sao."""
    if (a, b) in INTERACTION_SPECIFIC:
        return INTERACTION_SPECIFIC[(a, b)][0], INTERACTION_SPECIFIC[(a, b)][1]
    if (b, a) in INTERACTION_SPECIFIC:
        return INTERACTION_SPECIFIC[(b, a)][0], INTERACTION_SPECIFIC[(b, a)][1]
    tags_a, tags_b = _tags_of(a), _tags_of(b)
    for ta in tags_a:
        for tb in tags_b:
            rule = TAG_INTERACTION_RULES.get(frozenset({ta, tb}))
            if rule:
                return rule[0], rule[1]
    na = "cát" if _nature(a) in ("tốt", "cát") else ("xấu" if _nature(a) in ("xấu", "xấu-trung") else "trung")
    nb = "cát" if _nature(b) in ("tốt", "cát") else ("xấu" if _nature(b) in ("xấu", "xấu-trung") else "trung")
    key = (na, nb)
    if key in NATURE_RULES:
        r = NATURE_RULES[key]
        return r[0], r[1]
    return "phụ-thuộc", "tuỳ ngữ cảnh"


def pair_logic(a: str, b: str):
    """Logic đầy đủ cho một cặp sao (không phụ thuộc vị trí cung)."""
    name_a, name_b = _name(a), _name(b)
    rule = INTERACTION_SPECIFIC.get((a, b)) or INTERACTION_SPECIFIC.get((b, a))
    if rule is None:
        # tìm rule tag
        rule = None
        for ta in _tags_of(a):
            for tb in _tags_of(b):
                rule = TAG_INTERACTION_RULES.get(frozenset({ta, tb}))
                if rule:
                    break
            if rule:
                break
    if rule is None:
        na = "cát" if _nature(a) in ("tốt", "cát") else ("xấu" if _nature(a) in ("xấu", "xấu-trung") else "trung")
        nb = "cát" if _nature(b) in ("tốt", "cát") else ("xấu" if _nature(b) in ("xấu", "xấu-trung") else "trung")
        rule = NATURE_RULES.get((na, nb), ("phụ-thuộc", "tuỳ ngữ cảnh",
            f"{name_a} và {name_b}: tương tác trung tính, phụ thuộc cung đóng, cách cục và vận hạn.",
            "Nếu đặt đúng cung và có sao hỗ trợ, có thể phát huy.", 
            "Nếu đặt sai cung hoặc gặp hung tinh, dễ thành điểm yếu.",
            "Cần xét thêm đắc/hãm và hội chiếu."))

    cat, itype, ban, pos, neg, note = rule
    return {
        "star_a": a, "star_b": b,
        "star_a_name": name_a, "star_b_name": name_b,
        "category": cat,
        "interaction": itype,
        "ban_chat": ban.format(a=name_a, b=name_b),
        "positive": pos.format(a=name_a, b=name_b),
        "negative": neg.format(a=name_a, b=name_b),
        "note": note.format(a=name_a, b=name_b),
        "tags_a": sorted(_tags_of(a)), "tags_b": sorted(_tags_of(b)),
    }


def chart_stars(row, menh, only=None):
    """Toàn bộ sao trong một chart, gắn cung tương đối. `only` giới hạn danh sách khoá."""
    out = []
    for col, val in row.items():
        if not col.startswith("pos_") or val in ("", None, "-1"):
            continue
        try:
            pos = int(val)
        except (TypeError, ValueError):
            continue
        key = col[4:]
        if key not in LOGIC_STARS:
            continue
        if only is not None and key not in only:
            continue
        cung_index = (pos - menh) % 12
        out.append({"star": key, "name": _name(key), "cung_index": cung_index, "pos": pos,
                    "group": STAR_META.get(key, {}).get("group", ""),
                    "nature": _nature(key)})
    return out


def chart_interactions(row, menh, only=None):
    """Mọi cặp tương tác trong chart: sao–sao có quan hệ hoặc nhóm nổi tiếng."""
    stars = chart_stars(row, menh, only=only)
    by_key = {s["star"]: s for s in stars}
    items = []
    keys = [s["star"] for s in stars]
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            sa, sb = by_key[a], by_key[b]
            rel = relation(sa["pos"], sb["pos"])
            obj = pair_logic(a, b)
            obj["cung_a"] = sa["cung_index"]
            obj["cung_b"] = sb["cung_index"]
            obj["relation"] = rel
            obj["pruned"] = (rel == "không nối trực tiếp")
            items.append(obj)
    return items


def relation(a: int, b: int) -> str:
    a, b = a % 12, b % 12
    if a == b:
        return "cùng cung"
    if (a - b) % 12 == 6:
        return "xung chiếu"
    groups = [{0, 4, 8}, {1, 5, 9}, {3, 7, 11}, {2, 6, 10}]
    for g in groups:
        if a in g and b in g:
            return "tam hợp"
    return "không nối trực tiếp"
