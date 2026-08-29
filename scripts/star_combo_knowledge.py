# -*- coding: utf-8 -*-
"""
star_combo_knowledge.py
=======================
Cơ sở tri thức về BIẾN THỂ / TỔ HỢP của các sao khi kết hợp với nhau.

Khác với `star_cung_analysis` (một sao ở một cung), file này mô tả khi
**hai sao (hoặc bộ sao) gặp nhau** trong một lá số. Mỗi tổ hợp có:

  - `ban_chat`   : bản chất thật của tổ hợp (trung tính).
  - `positive`   : mặt tích cực rõ, có cơ sở.
  - `negative`   : mặt hạn chế / tiêu cực rõ, không nói giảm nói tránh.
  - `note`       : điều kiện đắc/hãm và bối cảnh làm tổ hợp mạnh/yếu.
  - `category`   : loại tổ hợp (tốt-đẹp, xung-khắc, tăng-lực, đào-hoa, ...).

Các tổ hợp được viết bằng khoá cột `pos_*` hoặc mã `star_key` (bỏ `pos_`).
Có dấu "+" nếu yêu cầu hai sao cùng CUNG; có dấu "?" nếu chỉ cần cùng TAM HỢP,
đối xung, hoặc kết nối trong lá số.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Trợ giúp để phân loại.
# --------------------------------------------------------------------------- #
def _combo(ban_chat, positive, negative, note="", category="tổ hợp"):
    return {
        "ban_chat": ban_chat,
        "positive": positive,
        "negative": negative,
        "note": note,
        "category": category,
    }


# --------------------------------------------------------------------------- #
# Khoá sao chuẩn hoá: dùng tên thanh ASCII như cột `pos_*` (bỏ `pos_`).
# --------------------------------------------------------------------------- #
COMBO_DATA = {
    # ------------------------------------------------------------------ #
    # Các tổ hợp "đẹp" nổi tiếng.
    # ------------------------------------------------------------------ #
    ("tu_vi", "thien_phu"): _combo(
        "Tử Vi và Thiên Phủ đối xứng (thủ Mệnh + thủ Thân hoặc hai cung tam hợp) — "
        "biểu trưng đế vương với kho tàng, quyền lực đi cùng của cải.",
        "Được quý nhân, quyền hành và tài sản; có khả năng lãnh đạo bền vững, việc lớn.",
        "Tự đắc, gia trưởng; dễ bị tiểu nhân bao vây; quá coi trọng địa vị nên mất lòng.",
        "Đắc địa ở Mệnh/Quan/Điền rất mạnh; gặp hung tinh dễ thành 'vua không ngai'.",
        "quyền-tài",
    ),
    ("thien_phu", "thien_tuong"): _combo(
        "Thiên Phủ (kho) + Thiên Tướng (bảo hộ): bộ 'Phủ Tướng' — an định, có cơ nghiệp.",
        "Ổn định, biết tổ chức, được người giúp đỡ; hợp quản lý tài chính.",
        "Thụ động, thích an toàn; thiếu quyết đoán khi cần đổi mới.",
        "Rất hợp Điền/Quan/Tài; gặp Lộc Tồn tăng của, gặp hung tinh giảm lực.",
        "an định",
    ),
    ("vu_khuc", "tham_lang"): _combo(
        "Vũ Khúc (tài) + Tham Lang (dục) đồng cung: 'Vũ Tham' — tham vọng tiền và quyền, "
        "tài năng thương mại.",
        "Nhanh nhạy, biết kiếm tiền, có tài đầu tư; thành công ở kinh doanh.",
        "Những lúc ham hố: tham lam, dùng thủ đoạn, làm giàu nhanh bại cũng nhanh.",
        "Đắc địa ở Thìn/Tuất/Sửu/Mùi càng mạnh; có Hỏa/Linh tăng nghị lực.",
        "tài-dục",
    ),
    ("tu_vi", "tham_lang"): _combo(
        "Tử Vi + Tham Lang: 'Tử Tham' — uy quyền gặp dục vọng, đế vương có tham vọng lớn.",
        "Bản lĩnh, có lãnh đạo, thích làm lớn; có thể phát tài phi thường.",
        "Quyền lực dễ thành quyền tham; tham quả sẽ mất uy, dễ bị phản.",
        "Cần có tài đức và người góp ý; gặp cát tinh mới thành quý.",
        "quyền-tham",
    ),
    ("tu_vi", "that_sat"): _combo(
        "Tử Vi + Thất Sát: 'Tử Sát' — quyền uy đi cùng sự quyết đoán, có khí phách chỉ huy.",
        "Mạnh mẽ, dám quyết, có sức mạnh chỉ huy; làm lớn trong môi trường kỷ luật.",
        "Cứng nhắc, độc đoán, dễ xung đột; quyền lực dễ bị lạm dụng.",
        "Rất hợp Quan/Điền; gặp hung tinh dễ thành bạo tàn.",
        "quyền-quyết",
    ),
    ("tu_vi", "pha_quan"): _combo(
        "Tử Vi + Phá Quân: 'Tử Phá' — quyền lực gặp phá cựu lập tân, dám lật đổ và dựng lại.",
        "Có tầm nhìn lớn, dám thay đổi, tạo được bước ngoặt lớn.",
        "Phá nhiều hơn xây; rủi ro cao, dễ mất sự ổn định nếu không kiểm soát.",
        "Cần có sự sẵn sàng về tài chính và thời cơ.",
        "bứt phá",
    ),
    ("thai_duong", "thai_am"): _combo(
        "Thái Dương + Thái Âm đồng cung hoặc xung chiếu: 'Nhật Nguyệt' — cân bằng sáng/âm, "
        "tự tin và tình cảm.",
        "Khôn ngoan, hài hoà, có phúc, giỏi giao tiếp và thấu cảm.",
        "Hay do dự, tính hai chiều; dễ mệt mỏi vì cân bằng thái quá.",
        "Đắc địa rất tốt; hãm địa dễ bi quan.",
        "âm-dương",
    ),
    ("thien_co", "thien_luong"): _combo(
        "Thiên Cơ (trí) + Thiên Lương (phúc) — 'Cơ Lương': tư duy cùng phước, cứu giải.",
        "Thông minh, có phước, dễ được cứu giúp; hợp nghề phân tích và tư vấn.",
        "Lo xa quá, hay băn khoăn; thương người quá mà mệt mình.",
        "Càng đắc càng tốt; gặp hung tinh giảm.",
        "trí-phúc",
    ),
    ("thien_dong", "thai_am"): _combo(
        "Thiên Đồng + Thái Âm: 'Đồng Âm' — hiền hoà và trăng thanh, sống tình cảm.",
        "Dễ chịu, có phúc, được yêu mến; hợp nghệ thuật, chăm sóc.",
        "Mềm yếu, hay buồn, thiếu tham vọng; dễ bị tình cảm chi phối.",
        "Đắc địa rất tốt; gặp hung tinh dễ tiêu cực.",
        "an-nhàn",
    ),
    ("thien_dong", "cu_mon"): _combo(
        "Thiên Đồng + Cự Môn: 'Đồng Cự' — hoà nhã gặp khẩu tài phản biện.",
        "Khéo giao tiếp, học nhanh; có khả năng giảng dạy, tranh luận.",
        "Thích biện luận, hay cãi vặt; tính tình thay đổi.",
        "Hãm địa dễ 'miệng quạ'; cần cẩn ngôn.",
        "khẩu-tài",
    ),
    ("thien_luong", "cu_mon"): _combo(
        "Thiên Lương + Cự Môn: 'Lương Cự' — phước gặp miệng, trí tuệ và hoạ giải.",
        "Thông minh, dạy đời; nói năng có sức thuyết phục, hay hoá giải thị phi.",
        "Hay diễn giải, khinh người; tự cho mình đúng, dễ mất lòng.",
        "Ở Mệnh hoặc Thân rất phát huy.",
        "luận-thuyết",
    ),
    ("thai_duong", "cu_mon"): _combo(
        "Thái Dương + Cự Môn: 'Nhật Cự' — ánh sáng và bóng tối, sáng suốt nhưng cũng đa nghi.",
        "Giỏi phát hiện vấn đề, nghề điều tra, luật, báo; có tiếng nói.",
        "Đa nghi, soi mói, dễ thị phi; cái sáng có thể thành quá đà.",
        "Đắc địa phát huy mạnh; hãm địa dễ cáu và mù quáng.",
        "nhật-cự",
    ),
    ("thai_am", "cu_mon"): _combo(
        "Thái Âm + Cự Môn: 'Âm Cự' — sâu kín gặp miệng lưỡi, nhạy cảm và phản biện.",
        "Sâu sắc, có trí nhớ tốt, hợp nghề nghiên cứu, tâm lý.",
        "Hay bực bội, khó tính, dễ giận dỗi; miệng lưỡi dễ đâm chọc.",
        "Hãm địa rất xấu; cần kiềm chế cảm xúc.",
        "ẩn-miệng",
    ),
    ("thai_duong", "that_sat"): _combo(
        "Thái Dương + Thất Sát: 'Nhật Sát' — nhiệt huyết và quyết liệt.",
        "Mạnh mẽ, quyết đoán, có sức nổ lực lớn; hợp kinh doanh, quân đội.",
        "Nóng nảy, dễ xung đột, bị hiểu lầm.",
        "Đắc địa có uy; hãm địa dễ thành hung hiểm.",
        "nhiệt-quyết",
    ),
    ("thai_duong", "thien_liang"): _combo(
        "Thái Dương + Thiên Lương: 'Nhật Lương' — sáng suốt và phước đức, hay giúp đời.",
        "Tốt bụng, hào hiệp, có uy tín; hợp nghề y, giáo, từ thiện.",
        "Ôm việc quá, mềm yếu, dễ bị lợi dụng lòng tốt.",
        "Gặp cát tinh rất tốt; hãm địa thiếu quyết đoán.",
        "phúc-hiệp",
    ),
    ("thai_am", "thien_liang"): _combo(
        "Thái Âm + Thiên Lương: 'Âm Lương' — nội tâm và phước, sống nhẹ nhàng.",
        "Hiền, có đức, vận may; thích cái đẹp và tâm linh.",
        "Thụ động, hay buồn, dễ lo xa; thiếu quyết đoán.",
        "Đắc địa có mọi điều tốt để sống an yên.",
        "tĩnh-phúc",
    ),
    ("lie_trinh", "that_sat"): _combo(
        "Liêm Trinh + Thất Sát: 'Liêm Sát' — sự cứng và mạnh, đồng cung hoặc tam hợp.",
        "Có khí phách, dám đối đầu, làm nghề quân, pháp, công an.",
        "Cực đoan, hung hãn; dễ tự hại và gây nạn.",
        "Rất cần cát tinh; không hợp chỗ yếu.",
        "kim-khí",
    ),
    # (bổ sung dùng hàm normalize phía dưới)
    ("lie_trinh", "pha_quan"): _combo(
        "Liêm Trinh + Phá Quân: 'Liêm Phá' — sự cứng rắn và phá phách.",
        "Mạnh, dám đổi mới; quyết liệt trong nghề.",
        "Phá hoại, thất thường, dễ làm mất thể diện.",
        "Cần sự tự chủ rất cao.",
        "quyết-liệt",
    ),
    # ------------------------------------------------------------------ #
    # Phụ tinh / yếu tố tăng-giảm.
    # ------------------------------------------------------------------ #
    ("loc_ton", "tu_vi"): _combo(
        "Lộc Tồn đi cùng Tử Vi: tài lộc gặp uy quyền, 'vua có kho'.",
        "Có tiền, có quyền, có phước; sống dư dả và được quý.",
        "Càng giàu càng dễ kiêu, bị nịnh và ganh.",
        "Đắc địa rất tốt; hãm cần cẩn thận.",
        "phú-quý",
    ),
    ("loc_ton", "thien_phu"): _combo(
        "Lộc Tồn + Thiên Phủ: lộc đi cùng kho tàng — cực thuận tài.",
        "Dồi dào tài sản, biết giữ của; sống sung túc.",
        "Có thể trở nên keo kiệt, nặng vật chất.",
        "Rất tốt ở Tài/Điền.",
        "đại-phú",
    ),
    ("loc_ton", "tham_lang"): _combo(
        "Lộc Tồn + Tham Lang: lộc gặp dục — tiền nhiều nhưng ham.",
        "Biết kiếm tiền, có cơ hội phát tài lớn.",
        "Tham lam, tiêu hoang; càng lộc càng dễ sa đà.",
        "Cần kiểm soát ham muốn.",
        "phú-tham",
    ),
    ("kinh_duong", "tu_vi"): _combo(
        "Kình Dương đi cùng Tử Vi: gai nhọn bên cạnh vua — quyền uy có lực cản.",
        "Bản lĩnh, cương trực, dám chống sai.",
        "Khó gần, hay tranh chấp, dễ mất lòng và gây hiềm khích.",
        "Tử Vi vẫn giữ được quyền nhưng phải đối đầu trắc trở.",
        "quyền-xung",
    ),
    ("da_la", "tu_vi"): _combo(
        "Đà La đi cùng Tử Vi: sự trì trệ bên vua — quyền nhưng chậm.",
        "Kiên trì, không nản, có chính kiến.",
        "Hay bị cản trở, nợ nần, khó khăn kéo dài.",
        "Phải nhẫn nại và tránh quyết định vội.",
        "quyền-trệ",
    ),
    ("hoa_tinh", "tham_lang"): _combo(
        "Hỏa Tinh + Tham Lang: 'Hỏa Tham' — lửa đốt lòng tham, nghị lực bốc cao.",
        "Đắc địa: nhiệt huyết, ham làm ăn, có thành công lớn.",
        "Hãm địa: nóng, thô, dễ mất bình tĩnh và gây rủi ro.",
        "Cách này mạnh ở Mệnh/Quan; phải có lý trí.",
        "hoả-tham",
    ),
    ("linh_tinh", "tham_lang"): _combo(
        "Linh Tinh + Tham Lang: 'Linh Tham' — ma thuật, sắc sảo.",
        "Thông minh, có duyên nghệ thuật, quyết đoán.",
        "Ám muội, đa nghi, dễ lợi dụng thủ đoạn.",
        "Đắc địa thành tài; hãm thành hung.",
        "linh-tham",
    ),
    ("van_xuong", "van_khuc"): _combo(
        "Văn Xương + Văn Khúc: 'Xương Khúc' — học vấn, văn chương",
        "Thông minh, học giỏi, có tài văn chương; đường công danh tốt.",
        "Dễ tài hoa mà phận, hay lo xa; gặp hoá kỵ dễ rối trí.",
        "Ở Mệnh/Quan/Tài rất thuận; gặp hoàn cảnh thuận lợi phát huy cao.",
        "văn-học",
    ),
    ("thien_khoi", "thien_viet"): _combo(
        "Thiên Khôi + Thiên Việt: 'Khôi Việt' — bộ quý nhân, đỡ vấp ngã.",
        "Gặp quý nhân, học hành, công danh thuận; tai qua nạn khỏi.",
        "Phụ thuộc người khác; dễ được giúp mà thiếu tự lực.",
        "Ở Mệnh/Quan rất tốt; hỗ trợ cả vận hạn.",
        "quý-nhân",
    ),
    ("dao_hoa", "hong_loan"): _combo(
        "Đào Hoa + Hồng Loan: 'Đào Loan' — tình duyên rực rỡ.",
        "Có sức hút, duyên tình thuận, hợp kết hôn, làm nghề liên quan đẹp.",
        "Đào hoa quá mạnh: dễ ngoại tình, thị phi, hao tiền vì tình.",
        "Ở Phu Thê vừa tốt vừa cần kiềm chế.",
        "đào-hoa",
    ),
    ("dao_hoa", "thien_ma"): _combo(
        "Đào Hoa + Thiên Mã: tình duyên và di chuyển — tình đi xa.",
        "Duyên tình mới, thú vị; gặp người khác nơi khác.",
        "Tình cảm không ổn, đi lại vất vả, dễ bỏ lỡ.",
        "Cần cân bằng tình và việc.",
        "phiêu-du",
    ),
    ("hoa_loc", "tu_vi"): _combo(
        "Hóa Lộc tọa Tử Vi: quyền được thêm lộc, như 'vua được kho'.",
        "Tiền và quyền song hành, thành công lớn.",
        "Càng nhiều quyền lộc càng dễ mất phương hướng nếu không đức.",
        "Rất tốt ở Mệnh/Quan",
        "đế-lộc",
    ),
    ("hoa_ky", "tu_vi"): _combo(
        "Hóa Kỵ tọa Tử Vi: quyền bị vướng bận, thành nhưng vất vả.",
        "Có quyền thật nhưng nhọc công; biết vượt khó sẽ được.",
        "Lo âu, gánh nặng, dễ mất của vì lụy quyền.",
        "Hóa Kỵ làm đế tinh giảm sức.",
        "đế-kỵ",
    ),
    ("hoa_ky", "thal_am"): _combo(
        "Hóa Kỵ tọa Thái Âm: tình cảm và tài lộc có vướng.",
        "Trân trọng cảm xúc, biết lo xa.",
        "Lo buồn, hao tài, dễ bi quan.",
        "Cần học cách buông bỏ.",
        "âm-kỵ",
    ),
    # ------------------------------------------------------------------ #
    # Bộ đôi xung khắc / biến thể chung.
    # ------------------------------------------------------------------ #
    ("cu_mon", "that_sat"): _combo(
        "Cự Môn + Thất Sát: miệng sắc gặp tay mạnh.",
        "Sắc sảo, quyết đoán khi làm đúng.",
        "Nói và làm đều nóng; dễ bệnh miệng, thị phi, xung đột.",
        "Cần rèn kiềm chế.",
        "khẩu-xung",
    ),
    ("cu_mon", "kinh_duong"): _combo(
        "Cự Môn + Kình Dương: lưỡi dao cạnh miệng.",
        "Đấu tranh, phản biện mạnh mẽ.",
        "Hay cãi cọ, tự hại, kết oán.",
        "Rất cần cẩn ngôn.",
        "thị-phi",
    ),
    ("cu_mon", "da_la"): _combo(
        "Cự Môn + Đà La: miệng và sự rào cản.",
        "Dai dẳng, có sức chịu đựng.",
        "Tranh chấp kéo dài, nợ miệng.",
        "Cần tránh dây dưa.",
        "cản-trở",
    ),
    ("that_sat", "pha_quan"): _combo(
        "Thất Sát + Phá Quân: 'Sát Phá' — mạnh và phá, đầy nhiệt.",
        "Làm lớn, dám thay đổi, táo bạo.",
        "Bạo, dễ nổ, phá tiền và phá quan hệ.",
        "Phải có kỷ luật thép.",
        "phá-hại",
    ),
    ("that_sat", "thien_tuong"): _combo(
        "Thất Sát + Thiên Tướng: bộ 'Sát Tướng' — mạnh có chỉ huy.",
        "Có khả năng lãnh đạo kỷ luật, quân đội, công an.",
        "Thiếu mềm mỏng, cương quá.",
        "Kết hợp tốt ở Quan/Điền.",
        "oai phong",
    ),
    ("pha_quan", "thien_tuong"): _combo(
        "Phá Quân + Thiên Tướng: 'Phá Tướng' — đổi mới có người bảo.",
        "Bứt phá nhưng có nền tảng, dễ phát triển.",
        "Vẫn còn thất thường, hay thay đổi kế hoạch.",
        "Cần người cố vấn ổn định.",
        "đổi-tướng",
    ),
    ("lie_trinh", "thien_phu"): _combo(
        "Liêm Trinh + Thiên Phủ: 'Liêm Phủ' — cương có nơi chứa.",
        "Có chức quyền và tài sản, biết dữ.",
        "Cương quá dễ khó nghe; của nhiều dễ thành ách.",
        "Đắc địa rất tốt ở Tài/Quan.",
        "liêm-phủ",
    ),
    ("lie_trinh", "thien_tuong"): _combo(
        "Liêm Trinh + Thiên Tướng: 'Liêm Tướng'.",
        "Hàm hạnh, văn võ, có sức thuyết phục.",
        "Khó tính, kén người.",
        "Kết hợp rất tốt ở Mệnh/Quan; gặp văn tinh và quý nhân càng phát huy.",
        "liêm-tướng",
    ),
}


# --------------------------------------------------------------------------- #
# Chuẩn hoá khoá sao: chấp nhận alias (thal_am -> thai_am, lie_trinh -> liem_trinh...).
# --------------------------------------------------------------------------- #
_ALIAS = {
    "thal_am": "thai_am",
    "thien_liang": "thien_luong",
    "lie_trinh": "liem_trinh",
    "tuvi": "tu_vi",
    "thiendong": "thien_dong",
    "that_sat": "that_sat",
}


def normalize_key(k: str) -> str:
    return _ALIAS.get(k, k)


def _normalize_combo_map():
    out = {}
    for (a, b), obj in COMBO_DATA.items():
        out[(normalize_key(a), normalize_key(b))] = obj
    return out


COMBO_DATA = _normalize_combo_map()
_KEYS_SET = set(COMBO_DATA.keys())


def add_combo(pair, obj):
    """Thêm/ghi đè một tổ hợp khi gọi từ bên ngoài."""
    a, b = pair
    COMBO_DATA[(normalize_key(a), normalize_key(b))] = obj


# --------------------------------------------------------------------------- #
# Quan hệ giữa các cặp (dùng xác định cùng cung / tam hợp / đối xung).
# --------------------------------------------------------------------------- #
TAM_HOP_GROUPS = [
    (0, 4, 8),   # Dần Ngọ Tuất
    (1, 5, 9),   # Mão Mùi Hợi
    (3, 7, 11),  # Tỵ Dậu Sửu
    (2, 6, 10),  # Thìn Thân Tý
]


def in_same_group(a: int, b: int) -> bool:
    for g in TAM_HOP_GROUPS:
        if a in g and b in g:
            return True
    return False


def is_opposite(a: int, b: int) -> bool:
    return (a - b) % 12 == 6


def relation(a: int, b: int) -> str:
    if a == b:
        return "cùng cung"
    if is_opposite(a, b):
        return "xung chiếu"
    if in_same_group(a, b):
        return "tam hợp"
    return "không nối trực tiếp"
