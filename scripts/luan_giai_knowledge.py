# -*- coding: utf-8 -*-
"""
luan_giai_knowledge.py
======================
Tầng TRI THỨC LUẬN GIẢI (rule-based "giống AI") cho kho Tử Vi 518.400 lá số.

Khác với star_knowledge_data.py (chỉ mô tả "sao ở cung"), file này chứa:

  - STAR_PROFILE   : hồ sơ 14 chính tinh theo lĩnh vực (tính cách, sự nghiệp,
                     tài lộc, tình duyên, sức khoẻ, lưu ý).
  - CUNG_PROFILE   : hồ sơ 12 cung (phạm vi, tích cực, hạn chế, khuyến nghị).
  - CUC_PROFILE    : ý nghĩa 5 cục (Thủy/Mộc/Kim/Thổ/Hỏa).
  - TUA_HOA_PROFILE: ý nghĩa Tứ Hoá.
  - CACH_RULES     : danh sách cách cục + điều kiện kích hoạt.
  - LUAN_RULES     : các quy tắc luận tổng hợp.

Engine sinh bài luận giải nằm ở scripts/luan_giai_chart.py.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Lĩnh vực trong một lá số.
# --------------------------------------------------------------------------- #
FIELDS = ["tinh_cach", "su_nghiep", "tai_loc", "tinh_duyen", "suc_khoe"]

FIELD_VI = {
    "tinh_cach": "Tính cách",
    "su_nghiep": "Sự nghiệp",
    "tai_loc": "Tài lộc",
    "tinh_duyen": "Tình duyên",
    "suc_khoe": "Sức khoẻ",
}

# --------------------------------------------------------------------------- #
# Hồ sơ 14 chính tinh.
# --------------------------------------------------------------------------- #
STAR_PROFILE = {
    "tu_vi": {
        "name": "Tử Vi", "element": "Thổ", "nature": "cát",
        "about": "Đế tinh, tượng trưng uy quyền, phẩm cách, sự đứng đắn và bề thế.",
        "tinh_cach": "Tự tin, có chính kiến, đứng đắn, nhưng dễ gia trưởng và hơi cô độc.",
        "su_nghiep": "Hợp lãnh đạo, quản lý, hành chính, tổ chức; làm lớn nếu có cấp dưới và quý nhân.",
        "tai_loc": "Tiền của ổn định về lâu dài; biết giữ cơ nghiệp, hợp đầu tư bất động sản.",
        "tinh_duyen": "Bạn đời đàng hoàng, đáng tin; dễ có nhiều người ngưỡng mộ.",
        "suc_khoe": "Nhìn chung khoẻ; về già chú ý huyết áp, gan, tim mạch.",
        "note": "Gặp nhiều cát tinh hội chiếu càng quý; gặp hung tinh dễ thành 'ốc nhĩ' (tên hay nhưng bị lay chuyển).",
    },
    "thien_co": {
        "name": "Thiên Cơ", "element": "Mộc", "nature": "cát",
        "about": "Sao mưu lược, thông minh, biến hoá, hay suy tính.",
        "tinh_cach": "Thông minh, nhạy bén, thích nghi, sâu sắc, hiếu học.",
        "su_nghiep": "Hợp nghề trí óc, nghiên cứu, kỹ thuật, phân tích, tư vấn, báo chí.",
        "tai_loc": "Kiếm tiền bằng trí tuệ; cần tính toán kỹ, tránh đầu cơ.",
        "tinh_duyen": "Duyên tình lý trí, hay lo nghĩ; nên chia sẻ nhiều hơn.",
        "suc_khoe": "Chú ý thần kinh, tiêu hoá, mất ngủ do lo nghĩ.",
        "note": "Thiên Cơ hợp với Hóa Quyền, Văn Xương, Văn Khúc; kỵ gặp nhiều hung tinh.",
    },
    "thai_duong": {
        "name": "Thái Dương", "element": "Hỏa", "nature": "cát",
        "about": "Mặt trời – quang minh, danh dự, hào hiệp, toả sáng.",
        "tinh_cach": "Rộng rãi, chân thành, nhiệt huyết, tích cực, dễ nổi bật.",
        "su_nghiep": "Hợp công vụ, hành chính, giáo dục, y tế, từ thiện, chính trị.",
        "tai_loc": "Tiền từ công việc minh bạch, danh tiếng; dễ được đề bạt.",
        "tinh_duyen": "Nam mệnh dễ được phụ nữ quý; nữ mệnh dễ gặp chuyện bạn đời.",
        "suc_khoe": "Chú ý mắt, tim mạch; phụ nữ cẩn hoả vượng.",
        "note": "Đóng ngày sáng (cung dương) phát huy tốt; ban đêm giảm lực.",
    },
    "vu_khuc": {
        "name": "Vũ Khúc", "element": "Kim", "nature": "cát",
        "about": "Sao tài chính, cương nghị, nguyên tắc, tháo vát.",
        "tinh_cach": "Kỷ luật, thực dụng, mạnh mẽ, quyết đoán, giữ chữ tín.",
        "su_nghiep": "Hợp kinh doanh, tài chính, kế toán, kỹ thuật, quản lý.",
        "tai_loc": "Rất mạnh về tiền; biết tính toán và giữ của.",
        "tinh_duyen": "Yêu bằng lý trí; cần chú ý thẳng thắn quá mức.",
        "suc_khoe": "Chú ý xương khớp, răng miệng, cột sống.",
        "note": "Đắc địa ở Thân, Dậu, Tỵ, Sửu; kỵ gặp Kình Dương, Đà La.",
    },
    "thien_dong": {
        "name": "Thiên Đồng", "element": "Thủy", "nature": "cát",
        "about": "Sao phúc lành, hoà nhã, ổn định, hưởng thụ.",
        "tinh_cach": "Hiền lành, dễ gần, có lòng nhân, thích an nhàn.",
        "su_nghiep": "Hợp dịch vụ, y tế, giáo dục, nghệ thuật, công việc chăm sóc.",
        "tai_loc": "Tiền đến đều nhưng không lớn; cần tiết chế chi tiêu.",
        "tinh_duyen": "Tình cảm ấm áp, dễ có cuộc sống hôn nhân êm ấm.",
        "suc_khoe": "Chú ý thận, bàng quang, tiểu đường; bệnh dễ kéo dài.",
        "note": "Giảm nhẹ phần lớn hung tinh; kỵ gặp Thái Âm hãm địa.",
    },
    "liem_trinh": {
        "name": "Liêm Trinh", "element": "Hỏa", "nature": "cát-hung",
        "about": "Liêm khiết, cứng rắn, có khí phách nhưng dễ bộc trực.",
        "tinh_cach": "Ngay thẳng, bản lĩnh, cầu toàn; dễ cực đoan, khó nhượng bộ.",
        "su_nghiep": "Hợp pháp luật, công an, quân đội, nghệ thuật, kỹ nghệ.",
        "tai_loc": "Tiền nhiều đến rồi đi; cần làm việc chân chính.",
        "tinh_duyen": "Duyên tình nồng nhưng nhiều thử thách, dễ tình tay ba.",
        "suc_khoe": "Chú ý máu, nội tiết, phụ nữ, da liễu.",
        "note": "Hãm địa rất xấu nếu gặp Thất Sát, Kình Dương; đắc địa thì có phẩm cao.",
    },
    "thien_phu": {
        "name": "Thiên Phủ", "element": "Thổ", "nature": "cát",
        "about": "Kho tàng, phú quý, bảo thủ, giữ gìn.",
        "tinh_cach": "Trầm ổn, thực tế, cẩn trọng, có gu thẩm mỹ.",
        "su_nghiep": "Hợp ngân hàng, tài chính, quản lý, tổ chức, bất động sản.",
        "tai_loc": "Có kho, có vốn; giỏi tích luỹ và giữ tài sản.",
        "tinh_duyen": "Bạn đời thực tế, chín chắn, biết lo toan.",
        "suc_khoe": "Chú ý tiêu hoá, dạ dày, mỡ máu.",
        "note": "Cấu tạo 'phủ tướng, tướng phủ' rất tốt; kỵ Tuần Triệt.",
    },
    "thai_am": {
        "name": "Thái Âm", "element": "Thủy", "nature": "cát",
        "about": "Mặt trăng – tình cảm, nội tâm, may mắn âm thầm.",
        "tinh_cach": "Nhạy cảm, dịu dàng, có trực giác, thích nghệ thuật.",
        "su_nghiep": "Hợp văn phòng, giáo dục, y tế, tâm lý, nghệ thuật, chăm sóc.",
        "tai_loc": "Tiền đến lặng lẽ, có của hồi môn, của âm phù.",
        "tinh_duyen": "Điểm yếu là dễ đa sầu đa cảm; hôn nhân cần chân thành.",
        "suc_khoe": "Chú ý máu, tiết chế ẩm thực, phụ nữ chú ý bệnh phụ khoa.",
        "note": "Đắc địa ban đêm; lạnh nhạt nếu gặp nhiều hung tinh.",
    },
    "tham_lang": {
        "name": "Tham Lang", "element": "Mộc", "nature": "cát-hung",
        "about": "Dục vọng, năng động, thông minh, nghệ thuật.",
        "tinh_cach": "Thông minh, nhạy cảm, ham muốn mạnh, dễ cám dỗ.",
        "su_nghiep": "Hợp thương mại, giải trí, nghệ thuật, thẩm mỹ, đầu tư.",
        "tai_loc": "Tiền nhiều, tiêu mạnh; thành công nếu biết tiết chế.",
        "tinh_duyen": "Duyên tình nồng, dễ đa tình; cần chung thuỷ.",
        "suc_khoe": "Chú ý gan, mỡ máu, bệnh do ăn chơi.",
        "note": "Đắc địa rất thông minh; gặp Hỏa Tinh, Linh Tinh biến thành nghị lực.",
    },
    "cu_mon": {
        "name": "Cự Môn", "element": "Thủy", "nature": "cát-hung",
        "about": "Khẩu tài, đa nghi, trí tuệ, hay tranh luận.",
        "tinh_cach": "Sắc bén, nói giỏi, hay lo nghĩ, dễ nghi ngờ.",
        "su_nghiep": "Hợp luật, truyền thông, giáo dục, nghiên cứu, tâm lý.",
        "tai_loc": "Tiền từ nghề miệng, tri thức; dễ thị phi tài chính.",
        "tinh_duyen": "Duyên cãi vã nhiều; cần lắng nghe.",
        "suc_khoe": "Chú ý phổi, đại tràng, dạ dày, thần kinh.",
        "note": "Cự Môn hoạ giải khi có Thiên Lương; kỵ Thái Âm.",
    },
    "thien_tuong": {
        "name": "Thiên Tướng", "element": "Thủy", "nature": "cát",
        "about": "Tướng mạo, trí tuệ, trợ giúp, chuẩn mực.",
        "tinh_cach": "Điềm đạm, biết lắng nghe, có sức thuyết phục.",
        "su_nghiep": "Hợp quan chức, tư vấn, giáo dục, y tế, ngoại giao.",
        "tai_loc": "Tiền ổn định; thích giúp đỡ người khác.",
        "tinh_duyen": "Bạn đời chuẩn mực, được trọng vọng.",
        "suc_khoe": "Khoẻ; chú ý bệnh nhẹ do lao lực.",
        "note": "Thiên Tướng làm tướng tốt cần có quyền; kỵ yếu địa.",
    },
    "thien_luong": {
        "name": "Thiên Lương", "element": "Mộc", "nature": "cát",
        "about": "Phúc tinh, cứu giải, trưởng giả, thanh cao.",
        "tinh_cach": "Hiền từ, bao dung, có đạo đức, thích giúp người.",
        "su_nghiep": "Hợp giáo dục, y, luật, tư pháp, từ thiện.",
        "tai_loc": "Tiền vừa phải; hay giúp nên dễ thiếu.",
        "tinh_duyen": "Tình duyên ổn, trân trọng nhau.",
        "suc_khoe": "Có bệnh dễ khỏi; chú ý đường tiêu hoá.",
        "note": "Thiên Lương cứu hung tinh rất tốt.",
    },
    "that_sat": {
        "name": "Thất Sát", "element": "Kim", "nature": "cát-hung",
        "about": "Quyết đoán, mạnh mẽ, hành động nhanh.",
        "tinh_cach": "Bản lĩnh, độc lập, cương quyết, hơi nóng.",
        "su_nghiep": "Hợp quân, công an, kinh doanh, nghề mạo hiểm, chỉ huy.",
        "tai_loc": "Có thể giàu nhanh nhưng sóng gió.",
        "tinh_duyen": "Tình duyên nóng bỏng nhưng thiếu dịu dàng.",
        "suc_khoe": "Dễ tai nạn, chấn thương; nên cẩn thận.",
        "note": "Đắc địa có nghị lực phi thường; kỵ Kình Dương, Đà La.",
    },
    "pha_quan": {
        "name": "Phá Quân", "element": "Thủy", "nature": "cát-hung",
        "about": "Phá cựu lập tân, tự do, bất khuất.",
        "tinh_cach": "Táo bạo, mạo hiểm, thích đổi mới, không thích gò bó.",
        "su_nghiep": "Hợp khởi nghiệp, xây dựng, thương mại, nghề mới.",
        "tai_loc": "Tiền vào nhanh, mất nhanh; cần kế hoạch.",
        "tinh_duyen": "Duyên tình nhiều biến động, cần bền bỉ.",
        "suc_khoe": "Chú ý dạ dày, thận, tai nạn.",
        "note": "Phá Quân + kiểm soát tốt sẽ có đại thành.",
    },
}


# --------------------------------------------------------------------------- #
# Hồ sơ 12 cung (index tương đối 0..11 so với Mệnh).
# --------------------------------------------------------------------------- #
CUNG_PROFILE = {
    0: ("Mệnh", "bản thân, tính cách, năng lực, định mệnh",
        "Mạnh về nhân sinh quan, học hỏi, tạo dựng chính mình",
        "Dễ ảnh hưởng bởi cảm xúc và quan niệm của bản thân",
        "Xây dựng giá trị cá nhân rõ ràng và giữ vững tinh thần."),
    1: ("Phụ Mẫu", "cha mẹ, trưởng bối, tổ tiên, học vấn gốc",
        "Được gia đình giúp đỡ, có nền tảng học vấn",
        "Bị ràng buộc gia đình, nghiêm khắc",
        "Biết ơn cha mẹ, học từ người đi trước."),
    2: ("Phúc Đức", "phúc khí, tâm linh, tinh thần, hưởng thụ",
        "Có phước, sống an nhàn, tâm linh tốt",
        "Dễ mềm lòng, thiếu kiên quyết",
        "Giữ tâm an, làm thiện, hưởng phúc có chừng."),
    3: ("Điền Trạch", "nhà cửa, đất đai, tổ nghiệp, cơ nghiệp",
        "Có đất có nhà, tài sản ổn định",
        "Liên quan tranh chấp, đầu tư rủi ro",
        "Quản lý giấy tờ, mua bán rõ ràng."),
    4: ("Quan Lộc", "sự nghiệp, công danh, quyền lực, học chuyên môn",
        "Có cơ hội thăng tiến, quyền hạn",
        "Áp lực công việc, cạnh tranh",
        "Trau dồi chuyên môn, giữ mối quan hệ."),
    5: ("Nô Bộc", "bạn bè, đồng nghiệp, người dưới quyền, tập thể",
        "Được người giúp, có hội nhóm mạnh",
        "Dễ phản bội, thị phi",
        "Chọn bạn mà chơi, đề phòng lừa đảo."),
    6: ("Thiên Di", "đi xa, người ngoài, xuất ngoại, môi trường rộng",
        "Ra ngoài phát triển, gặp quý nhân",
        "Rủi ro khi đi xa, bất đồng",
        "Mở rộng mối quan hệ, cẩn trọng hành trình."),
    7: ("Tật Ách", "sức khoẻ, bệnh tật, tai nạn, lo âu",
        "Nếu cát thì ít bệnh, biết cách chăm sóc",
        "Chịu đựng căng thẳng, bệnh âm thầm",
        "Khám sức khoẻ định kỳ, sống điều độ."),
    8: ("Tài Bạch", "tiền bạc, tài chính, thu nhập, kinh doanh",
        "Có của, biết kiếm tiền, giữ vốn",
        "Dễ thất thoát, tiêu xài, vay nợ",
        "Lập kế hoạch tài chính, tránh đầu cơ."),
    9: ("Tử Tức", "con cái, hậu vận, sự tiếp nối",
        "Con cái hiếu thuận, hậu vận có nơi nương",
        "Dễ xa con, lo con cái",
        "Chăm lo giáo dục, chuẩn bị tuổi già."),
    10: ("Phu Thê", "hôn nhân, vợ chồng, tình duyên",
        "Hôn nhân thuận, có người đồng hành",
        "Dễ tranh cãi, bất đồng, đào hoa",
        "Tôn trọng và lắng nghe đối phương."),
    11: ("Huynh Đệ", "anh chị em, bạn ruột, đồng môn",
        "Anh em hoà thuận, giúp nhau",
        "Dễ ganh tị, tranh quyền",
        "Giữ tình thân, phân minh tiền bạc."),
}


# --------------------------------------------------------------------------- #
# Hồ sơ 5 cục.
# --------------------------------------------------------------------------- #
CUC_PROFILE = {
    "Thủy Nhị Cục": {
        "so": 2, "hanh": "Thủy", "nature": "linh hoạt",
        "about": "Thông minh, mềm mỏng, biết thích nghi, giỏi giao tiếp.",
        "career": "Hợp nghề tri thức, dịch vụ, hành chính, ngoại giao, giao thương.",
        "tai": "Tiền đến từ quan hệ và sự khéo léo; cần giữ được lòng tin.",
        "tinh": "Duyên tình mềm mại, dễ cảm thông; nên chọn người ổn định.",
        "note": "Thủy dễ chảy, nên cần điểm dừng và nguyên tắc.",
    },
    "Mộc Tam Cục": {
        "so": 3, "hanh": "Mộc", "nature": "phát triển",
        "about": "Có sức phát triển, học hỏi, đam mê, dễ mềm yếu khi bị kìm hãm.",
        "career": "Hợp giáo dục, nghiên cứu, nghệ thuật, nông - lâm - môi trường.",
        "tai": "Tiền tăng dần nhờ tích luỹ, trí tuệ; cần kiên trì.",
        "tinh": "Tình cảm chân thành, trưởng thành theo thời gian.",
        "note": "Non phải tưới, trưởng phải tỉa; cần kỷ luật bản thân.",
    },
    "Kim Tứ Cục": {
        "so": 4, "hanh": "Kim", "nature": "cương nghị",
        "about": "Sắc sảo, nguyên tắc, quyết đoán, có năng lực sắp xếp.",
        "career": "Hợp kỹ thuật, tài chính, luật, quân đội, kế toán, chính xác.",
        "tai": "Kiếm tiền bằng năng lực và sự chính xác; dễ giữ của.",
        "tinh": "Tình duyên lý trí, cần học cách mềm mỏng.",
        "note": "Kim dễ cứng; nên rèn nhẫn nại và linh hoạt.",
    },
    "Thổ Ngũ Cục": {
        "so": 5, "hanh": "Thổ", "nature": "bền vững",
        "about": "Ổn định, trung thực, nặng tình, có khả năng gây dựng.",
        "career": "Hợp bất động sản, nông nghiệp, xây dựng, tổ chức, hành chính.",
        "tai": "Có của bền, nhờ cần cù; nên đầu tư lâu dài.",
        "tinh": "Tình duyên chắc chắn, ít thay đổi.",
        "note": "Thổ dễ chậm; cần hoạt bát hơn để không bỏ lỡ cơ hội.",
    },
    "Hỏa Lục Cục": {
        "so": 6, "hanh": "Hỏa", "nature": "nhiệt huyết",
        "about": "Nhiệt tình, sáng tạo, nhanh nhẹn, có sức truyền cảm.",
        "career": "Hợp nghề truyền thông, nghệ thuật, công nghệ, điện, marketing.",
        "tai": "Tiền đến nhanh, có thể mất nhanh; cần biết dừng.",
        "tinh": "Tình yêu nồng ấm, dễ bốc đồng; cần tiết chế.",
        "note": "Hoả cần đất để giữ; nên kết hợp với kế hoạch bền vững.",
    },
}


# --------------------------------------------------------------------------- #
# Tứ Hoá.
# --------------------------------------------------------------------------- #
TUA_HOA_PROFILE = {
    "hoa_loc": {
        "name": "Hóa Lộc", "meaning": "Lộc tinh, phát tài, thành công, niềm vui.",
        "good_field": "Cung có Hóa Lộc: tài năng và lợi ích được tăng cường.",
    },
    "hoa_quyen": {
        "name": "Hóa Quyền", "meaning": "Quyền tinh, địa vị, uy quyền, thăng tiến.",
        "good_field": "Cung có Hóa Quyền: chủ động, có trách nhiệm, dễ được bổ nhiệm.",
    },
    "hoa_khoa": {
        "name": "Hóa Khoa", "meaning": "Khoa tinh, danh vọng, học vấn, tài trí.",
        "good_field": "Cung có Hóa Khoa: học vấn, tiếng tốt, quý nhân giúp.",
    },
    "hoa_ky": {
        "name": "Hóa Kỵ", "meaning": "Kỵ tinh, ngăn trở, lo âu, hao tổn.",
        "good_field": "Cung có Hóa Kỵ: áp lực, bất an; cần chú ý và hoá giải.",
    },
}


# --------------------------------------------------------------------------- #
# Cách cục: điều kiện là hàm (chart dict) -> True/False. Mô tả có thể dùng
# để sinh đoạn văn riêng. Lưu dạng dữ liệu để build bảng (không trực tiếp hàm
# trong JSON): condition_text mô tả điều kiện.
# --------------------------------------------------------------------------- #
CACH_RULES = [
    {
        "ma": "TUVITHUMENH",
        "ten": "Tử Vi thủ Mệnh",
        "desc": "Có uy quyền, bản lĩnh, được kính trọng nhưng dễ đơn độc vì đứng cao.",
        "muc": "vua_menh",
        "condition": "Tử Vi tại cung Mệnh",
    },
    {
        "ma": "THAN_CU_MENH",
        "ten": "Thân cư Mệnh",
        "desc": "Mệnh Thân đồng cung – bản thân, vận mệnh và hành động gắn chặt với nhau; thành bại do mình.",
        "muc": "than_menh",
        "condition": "Thân tại cung Mệnh",
    },
    {
        "ma": "THAN_CU_QUAN",
        "ten": "Thân cư Quan Lộc",
        "desc": "Chú trọng công danh, sự nghiệp giữ vai trò trung tâm.",
        "muc": "than",
        "condition": "Thân tại Quan Lộc",
    },
    {
        "ma": "LOC_TAI_MENH",
        "ten": "Lộc Tồn tại Mệnh",
        "desc": "Lòng nhân từ, có tiền, được người quý; cuộc sống dư dả.",
        "muc": "cat_cach",
        "condition": "Lộc Tồn tại cung Mệnh",
    },
    {
        "ma": "LOC_TAI_TAI",
        "ten": "Lộc Tồn tại Tài Bạch",
        "desc": "Tài chính tốt, có của dự phòng, biết tích luỹ.",
        "muc": "cat_cach",
        "condition": "Lộc Tồn tại cung Tài Bạch",
    },
    {
        "ma": "VAN_XUONG_MENH",
        "ten": "Văn Xương/Văn Khúc tại Mệnh",
        "desc": "Thông minh, học rộng, có tài văn chương và cơ may học vấn.",
        "muc": "cat_cach",
        "condition": "Văn Xương hoặc Văn Khúc tại Mệnh",
    },
    {
        "ma": "KHOI_VIET_MENH",
        "ten": "Khôi Việt tại Mệnh",
        "desc": "Có quý nhân phù trợ, đường học vấn và sự nghiệp thuận lợi.",
        "muc": "cat_cach",
        "condition": "Thiên Khôi hoặc Thiên Việt tại Mệnh",
    },
    {
        "ma": "HOA_LOC_MENH",
        "ten": "Hóa Lộc tại Mệnh",
        "desc": "Tài năng, may mắn, có lộc từ chính bản thân.",
        "muc": "cat_cach",
        "condition": "Hóa Lộc tại cung Mệnh",
    },
    {
        "ma": "HOA_QUYEN_MENH",
        "ten": "Hóa Quyền tại Mệnh",
        "desc": "Có quyền hành, quyết đoán, dễ thăng tiến.",
        "muc": "cat_cach",
        "condition": "Hóa Quyền tại cung Mệnh",
    },
    {
        "ma": "HOA_KY_MENH",
        "ten": "Hóa Kỵ tại Mệnh",
        "desc": "Nội tâm nhiều trăn trở, bản thân chịu áp lực lớn; cần chăm sóc tinh thần.",
        "muc": "canh_bao",
        "condition": "Hóa Kỵ tại cung Mệnh",
    },
    {
        "ma": "HOA_LINH_MENH",
        "ten": "Hỏa/Linh tại Mệnh",
        "desc": "Nóng nảy, xung động; đắc địa thì mạnh mẽ, hãm địa thì dễ rủi ro.",
        "muc": "canh_bao",
        "condition": "Hỏa Tinh hoặc Linh Tinh tại Mệnh",
    },
    {
        "ma": "DAO_THOA_PHU_THE",
        "ten": "Đào Hoa tại Phu Thê",
        "desc": "Tình duyên quyến rũ, dễ hấp dẫn người khác; cần chung thuỷ.",
        "muc": "tinh_duyen",
        "condition": "Đào Hoa tại cung Phu Thê",
    },
    {
        "ma": "CU_MON_MENH",
        "ten": "Cự Môn tại Mệnh",
        "desc": "Miệng lưỡi sắc bén, hay tranh luận, cần cẩn ngôn.",
        "muc": "canh_bao",
        "condition": "Cự Môn tại cung Mệnh",
    },
    {
        "ma": "THAM_VU_DONG",
        "ten": "Vũ Tham đồng cung",
        "desc": "Mưu lược + tài chính: có năng lực kiếm tiền, linh hoạt nhưng dễ thay đổi.",
        "muc": "cach",
        "condition": "Vũ Khúc và Tham Lang cùng một cung",
    },
    {
        "ma": "PHU_TUONG",
        "ten": "Phủ Tướng đồng cung",
        "desc": "An định, có cơ nghiệp, được người giúp, hợp quản lý.",
        "muc": "cach",
        "condition": "Thiên Phủ và Thiên Tướng cùng một cung",
    },
    {
        "ma": "SAT_PHA",
        "ten": "Sát Phá đồng cung",
        "desc": "Hành động mạnh, có thể bứt phá lớn rồi lại chuyển dịch.",
        "muc": "cach",
        "condition": "Thất Sát và Phá Quân cùng một cung",
    },
]


# --------------------------------------------------------------------------- #
# Quy tắc luận tổng hợp.
# --------------------------------------------------------------------------- #
LUAN_RULES = [
    "Cách cục tổng thể quyết định 50% lá số; sao hội chiếu và đắc/hãm quyết định phần còn lại.",
    "Cung Mệnh + Thân + Cục là bộ ba cốt lõi để luận tính cách và vận mệnh.",
    "Tài Bạch, Quan Lộc, Phu Thê là ba cung dùng để rút gọn giai đoạn đời sống.",
    "Tật Ách luôn cần đối chiếu với Tử Tức và Phu Mẫu về vòng đời.",
    "Tứ Hoá ở cung nào làm nổi cung đó; Hóa Kỵ cần kết hợp với cát tinh để cân bằng.",
    "Vòng Trường Sinh cho biết giai đoạn vượng/suy của từng cung.",
    "Đánh giá sao qua đắc địa, hãm địa, hội/cụ, xung/chiếu trước khi kết luận.",
    "Không có lá số nào hoàn toàn tốt hoặc xấu; cần nêu mặt mạnh và hạn chế.",
]
