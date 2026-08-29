# -*- coding: utf-8 -*-
"""
tuvi_engine.py
==============
Một engine thuần Python (không phụ thuộc thư viện ngoài) để "an sao" một lá số
Tử Vi theo quy tắc Bắc phái phổ biến tại Việt Nam:

  - 12 cung cố định, cung Dần = vị trí 0.
  - Cung Mệnh / Thân theo tháng + giờ sinh.
  - Xác định Ngũ Hành Cục theo can năm + cung an Mệnh.
  - An sao Tử Vi theo ngày + số cục, rồi an 14 chính tinh.
  - An các phụ tinh theo can / chi năm, tháng, giờ, ngày và các vòng
    Trường Sinh, Thái Tuế, Lộc Tồn.

Mọi vị trí cung được lưu bằng chỉ số 0..11 theo thứ tự thuận chiều kim đồng hồ:
  Dần(0), Mão(1), Thìn(2), Tỵ(3), Ngọ(4), Mùi(5),
  Thân(6), Dậu(7), Tuất(8), Hợi(9), Tý(10), Sửu(11).

Giờ được lưu bằng chỉ số 0..11 với Tý = 0 (thứ tự Tý, Sửu, Dần, ... , Hợi).

Tài liệu nguồn và các lựa chọn trường phái được ghi trong docs/nguon-algorithm.md.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Bảng tên
# --------------------------------------------------------------------------- #
CAN_NAMES = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI_NAMES_CUNG = [
    "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi",
    "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu",
]
HOUR_NAMES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
              "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
# Tên 12 cung theo THỨ TỰ TƯƠNG ĐỐI, tính thuận chiều kim đồng hồ từ cung Mệnh:
# Mệnh → Phụ Mẫu → Phúc Đức → Điền Trạch → Quan Lộc → Nô Bộc → Thiên Di →
# Tật Ách → Tài Bạch → Tử Tức → Phu Thê → Huynh Đệ.
CUNG_10 = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc",
           "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]


def cung_label(pos: int, menh: int) -> str:
    """Tên cung tại vị trí `pos` khi Mệnh an tại `menh` (thuận chiều kim đồng hồ)."""
    return CUNG_10[(pos - menh) % 12]

CUC_NAMES = {
    2: "Thủy Nhị Cục",
    3: "Mộc Tam Cục",
    4: "Kim Tứ Cục",
    5: "Thổ Ngũ Cục",
    6: "Hỏa Lục Cục",
}
CUC_HANH = {2: "Thủy", 3: "Mộc", 4: "Kim", 5: "Thổ", 6: "Hỏa"}

# 60 hoa giáp theo thứ tự chuẩn. Số 0 = Giáp Tý.
SEXAGENARY = [
    "Giáp Tý", "Ất Sửu", "Bính Dần", "Đinh Mão", "Mậu Thìn", "Kỷ Tỵ",
    "Canh Ngọ", "Tân Mùi", "Nhâm Thân", "Quý Dậu", "Giáp Tuất", "Ất Hợi",
    "Bính Tý", "Đinh Sửu", "Mậu Dần", "Kỷ Mão", "Canh Thìn", "Tân Tỵ",
    "Nhâm Ngọ", "Quý Mùi", "Giáp Thân", "Ất Dậu", "Bính Tuất", "Đinh Hợi",
    "Mậu Tý", "Kỷ Sửu", "Canh Dần", "Tân Mão", "Nhâm Thìn", "Quý Tỵ",
    "Giáp Ngọ", "Ất Mùi", "Bính Thân", "Đinh Dậu", "Mậu Tuất", "Kỷ Hợi",
    "Canh Tý", "Tân Sửu", "Nhâm Dần", "Quý Mão", "Giáp Thìn", "Ất Tỵ",
    "Bính Ngọ", "Đinh Mùi", "Mậu Thân", "Kỷ Dậu", "Canh Tuất", "Tân Hợi",
    "Nhâm Tý", "Quý Sửu", "Giáp Dần", "Ất Mão", "Bính Thìn", "Đinh Tỵ",
    "Mậu Ngọ", "Kỷ Mùi", "Canh Thân", "Tân Dậu", "Nhâm Tuất", "Quý Hợi",
]

# Map từ chỉ số hoa giáp -> (can_index, chi_cung_index)
_SEXAGENARY_CAN = [i % 10 for i in range(60)]
_SEXAGENARY_CHI_CUNG = []
for name in SEXAGENARY:
    _, chi = name.split()
    _SEXAGENARY_CHI_CUNG.append(CHI_NAMES_CUNG.index(chi))

# --------------------------------------------------------------------------- #
# Danh sách 14 chính tinh.
# --------------------------------------------------------------------------- #
CHINH_TINH_NAMES = [
    "Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh",
    "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn",
    "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân",
]

TRANG_SINH_NAMES = [
    "Trường Sinh", "Dưỡng", "Thai", "Tuyệt", "Mộ", "Tử",
    "Bệnh", "Suy", "Đế Vượng", "Lâm Quan", "Quan Đới", "Mộc Dục",
]
THAI_TUE_NAMES = [
    "Thái Tuế", "Thiếu Dương", "Tang Môn", "Thiếu Âm", "Quan Phù", "Tử Phù",
    "Tuế Phá", "Long Đức", "Bạch Hổ", "Phúc Đức", "Điếu Khách", "Trực Phù",
]
LOC_TON_NAMES = [
    "Lộc Tồn", "Bác Sỹ", "Lực Sỹ", "Thanh Long", "Tiểu Hao", "Tướng Quân",
    "Tấu Thư", "Phi Liêm", "Hỷ Thần", "Bệnh Phù", "Đại Hao", "Phục Binh",
    "Quan Phủ",
]

# Tên Unicode tiếng Việt -> khoá cột ASCII (để dùng trong SQL/CSV).
STAR_ASCII_KEY = {
    "Tử Vi": "tu_vi",
    "Thiên Cơ": "thien_co",
    "Thái Dương": "thai_duong",
    "Vũ Khúc": "vu_khuc",
    "Thiên Đồng": "thien_dong",
    "Liêm Trinh": "liem_trinh",
    "Thiên Phủ": "thien_phu",
    "Thái Âm": "thai_am",
    "Tham Lang": "tham_lang",
    "Cự Môn": "cu_mon",
    "Thiên Tướng": "thien_tuong",
    "Thiên Lương": "thien_luong",
    "Thất Sát": "that_sat",
    "Phá Quân": "pha_quan",
    "Trường Sinh": "truong_sinh",
    "Dưỡng": "duong",
    "Thai": "thai",
    "Tuyệt": "tuyet",
    "Mộ": "mo",
    "Tử": "tu",
    "Bệnh": "benh",
    "Suy": "suy",
    "Đế Vượng": "de_vuong",
    "Lâm Quan": "lam_quan",
    "Quan Đới": "quan_doi",
    "Mộc Dục": "moc_duc",
    "Thái Tuế": "thai_tue",
    "Thiếu Dương": "thieu_duong",
    "Tang Môn": "tang_mon",
    "Thiếu Âm": "thieu_am",
    "Quan Phù": "quan_phu",
    "Tử Phù": "tu_phu",
    "Tuế Phá": "tue_pha",
    "Long Đức": "long_duc",
    "Bạch Hổ": "bach_ho",
    "Phúc Đức": "phuc_duc",
    "Điếu Khách": "dieu_khach",
    "Trực Phù": "truc_phu",
    "Lộc Tồn": "loc_ton",
    "Bác Sỹ": "bac_sy",
    "Lực Sỹ": "luc_sy",
    "Thanh Long": "thanh_long",
    "Tiểu Hao": "tieu_hao",
    "Tướng Quân": "tuong_quan",
    "Tấu Thư": "tau_thu",
    "Phi Liêm": "phi_liem",
    "Hỷ Thần": "hy_than",
    "Bệnh Phù": "benh_phu",
    "Đại Hao": "dai_hao",
    "Phục Binh": "phuc_binh",
    "Quan Phủ": "quan_phu",
}


def star_key(name: str) -> str:
    return STAR_ASCII_KEY[name]

# --------------------------------------------------------------------------- #
# Bảng Cục: can năm + cung an Mệnh.
# Cột: Tý-Sửu, Dần-Mão, Thìn-Tỵ, Ngọ-Mùi, Thân-Dậu, Tuất-Hợi.
# --------------------------------------------------------------------------- #
CUC_TABLE = [
    [2, 6, 3, 5, 4, 6],  # Giáp - Kỷ
    [6, 5, 4, 3, 2, 5],  # Ất - Canh
    [5, 3, 2, 4, 6, 3],  # Bính - Tân
    [3, 4, 6, 2, 5, 4],  # Đinh - Nhâm
    [4, 2, 5, 6, 3, 2],  # Mậu - Quý
]
_CAN_GROUP = [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]


def _cuc_column(menh_cung: int) -> int:
    """Trả về cột trong bảng Cục cho cung Mệnh."""
    if menh_cung in (10, 11):      # Tý, Sửu
        return 0
    if menh_cung in (0, 1):        # Dần, Mão
        return 1
    if menh_cung in (2, 3):        # Thìn, Tỵ
        return 2
    if menh_cung in (4, 5):        # Ngọ, Mùi
        return 3
    if menh_cung in (6, 7):        # Thân, Dậu
        return 4
    return 5                       # Tuất, Hợi


# --------------------------------------------------------------------------- #
# Bảng phụ tinh theo Can năm.
# Chỉ số cung theo thứ tự Dần=0..Sửu=11.
# --------------------------------------------------------------------------- #
LOC_TON_BY_CAN = [0, 1, 3, 4, 3, 4, 6, 7, 9, 10]
KINH_DUONG_BY_CAN = [1, 2, 4, 5, 4, 5, 7, 8, 10, 11]
DA_LA_BY_CAN = [11, 0, 2, 3, 2, 3, 5, 6, 8, 9]
QUANG_AN_BY_CAN = [8, 9, 11, 0, 11, 0, 2, 3, 5, 6]
DUONG_PHU_BY_CAN = [5, 6, 8, 9, 8, 9, 11, 0, 2, 3]
THIEN_KHOI_BY_CAN = [11, 10, 9, 9, 11, 10, 4, 4, 1, 1]
THIEN_VIET_BY_CAN = [5, 6, 7, 0, 5, 6, 0, 0, 3, 3]
THIEN_QUANG_BY_CAN = [5, 2, 3, 0, 1, 7, 9, 7, 8, 4]
THIEN_PHUC_BY_CAN = [7, 6, 10, 9, 1, 0, 4, 3, 4, 3]
LUU_HA_BY_CAN = [7, 8, 5, 2, 3, 4, 6, 1, 9, 0]
THIEN_TRU_BY_CAN = [3, 4, 10, 3, 4, 6, 0, 4, 7, 8]

# Tứ Hoá (theo Can năm): tên sao nhận Hoá.
HOA_LOC_BY_CAN = {
    0: "Liêm Trinh", 1: "Thiên Cơ", 2: "Thiên Đồng", 3: "Nguyệt Đức",
    4: "Tham Lang", 5: "Vũ Khúc", 6: "Thái Dương", 7: "Cự Môn",
    8: "Thiên Lương", 9: "Phá Quân",
}
HOA_QUYEN_BY_CAN = {
    0: "Phá Quân", 1: "Thiên Lương", 2: "Thiên Cơ", 3: "Thiên Đồng",
    4: "Nguyệt Đức", 5: "Tham Lang", 6: "Vũ Khúc", 7: "Thái Dương",
    8: "Tử Vi", 9: "Cự Môn",
}
HOA_KHOA_BY_CAN = {
    0: "Vũ Khúc", 1: "Tử Vi", 2: "Văn Xương", 3: "Thiên Cơ",
    4: "Hữu Bật", 5: "Thiên Lương", 6: "Thiên Đồng", 7: "Văn Khúc",
    8: "Tả Phù", 9: "Nguyệt Đức",
}
HOA_KY_BY_CAN = {
    0: "Thái Dương", 1: "Nguyệt Đức", 2: "Liêm Trinh", 3: "Cự Môn",
    4: "Thiên Cơ", 5: "Văn Khúc", 6: "Nguyệt Đức", 7: "Văn Xương",
    8: "Vũ Khúc", 9: "Tham Lang",
}

# --------------------------------------------------------------------------- #
# Bảng phụ tinh theo Chi năm. Thứ tự mảng theo chi năm:
# Tý,Sửu,Dần,Mão,Thìn,Tỵ,Ngọ,Mùi,Thân,Dậu,Tuất,Hợi
# (tương ứng chỉ số cung 10,11,0,1,2,3,4,5,6,7,8,9).
# --------------------------------------------------------------------------- #
LONG_TRI_BY_CHI = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1]
PHUONG_CAC_BY_CHI = [8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10, 9]
GIAI_THAN_BY_CHI = [8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10, 9]
THIEN_KHOC_BY_CHI = [4, 3, 2, 1, 0, 11, 10, 9, 8, 7, 6, 5]
THIEN_HU_BY_CHI = [4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3]
THIEN_DUC_BY_CHI = [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6]
NGUYET_DUC_BY_CHI = [3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2]
HONG_LOAN_BY_CHI = [1, 0, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
THIEN_HY_BY_CHI = [7, 6, 5, 4, 3, 2, 1, 0, 11, 10, 9, 8]
CO_THAN_BY_CHI = [0, 0, 3, 3, 3, 6, 6, 6, 9, 9, 9, 0]
QUA_TU_BY_CHI = [8, 8, 11, 11, 11, 2, 2, 2, 5, 5, 5, 8]
DAO_HOA_BY_CHI = [7, 4, 1, 10, 7, 4, 1, 10, 7, 4, 1, 10]
THIEN_MA_BY_CHI = [0, 9, 6, 3, 0, 9, 6, 3, 0, 9, 6, 3]
KIEP_SAT_BY_CHI = [3, 0, 9, 6, 3, 0, 9, 6, 3, 0, 9, 6]
HOA_CAI_BY_CHI = [2, 11, 8, 5, 2, 11, 8, 5, 2, 11, 8, 5]
PHA_TOAI_BY_CHI = [3, 11, 7, 3, 11, 7, 3, 11, 7, 3, 11, 7]
THIEN_KHONG_BY_CHI = [11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Chi năm -> cung khởi Hỏa Tinh, Linh Tinh (trường phái Bắc phái thông dụng:
# Tỵ-Dậu-Sửu khởi Hỏa tại Mão, Linh tại Tuất).
HOA_LINH_KHOI = {
    tuple([10, 11, 2]): (11, 1),   # Thân, Tý, Thìn -> Hỏa Dần, Linh Tuất
    tuple([0, 4, 8]): (11, 1),     # Dần, Ngọ, Tuất -> Hỏa Sửu, Linh Mão
    tuple([3, 7, 11]): (1, 8),     # Tỵ, Dậu, Sửu -> Hỏa Mão, Linh Tuất
    tuple([9, 1, 5]): (7, 8),      # Hợi, Mão, Mùi -> Hỏa Dậu, Linh Tuất
}

# --------------------------------------------------------------------------- #
# Bảng phụ tinh theo tháng sinh (mảng index tháng 1..12).
# --------------------------------------------------------------------------- #
TA_PHU_BY_MONTH = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1]
HUU_BAT_BY_MONTH = [8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10, 9]
THIEN_HINH_BY_MONTH = [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6]
THIEN_DIEU_BY_MONTH = [11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
THIEN_Y_BY_MONTH = [11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
THIEN_GIAI_BY_MONTH = [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5]
DIA_GIAI_BY_MONTH = [5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4]

# --------------------------------------------------------------------------- #
# Bảng phụ tinh theo giờ sinh (index giờ Tý=0..Hợi=11).
# --------------------------------------------------------------------------- #
VAN_XUONG_BY_HOUR = [8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10, 9]
VAN_KHUC_BY_HOUR = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1]
THAI_PHU_BY_HOUR = [4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3]
PHONG_CAO_BY_HOUR = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
DIA_KHONG_BY_HOUR = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10]
DIA_KIEP_BY_HOUR = [9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8]

# Tuần Không: theo 10 hoa giáp -> cung Tuần; Triệt theo nhóm can.
TUAN_BY_TUAN = [8, 6, 4, 2, 0, 10]
TRIET_BY_CAN = {
    0: (6, 7), 1: (4, 5), 2: (2, 3), 3: (0, 1), 4: (10, 11),
    5: (6, 7), 6: (4, 5), 7: (2, 3), 8: (0, 1), 9: (10, 11),
}


def add(idx: int, n: int) -> int:
    return (idx + n) % 12


def sub(idx: int, n: int) -> int:
    return (idx - n) % 12


# --------------------------------------------------------------------------- #
# Các hàm thành phần.
# --------------------------------------------------------------------------- #
def cung_menh_than(month: int, hour_index: int):
    """
    month: 1..12 âm lịch.
    hour_index: 0=Tý..11=Hợi.
    Trả về (cung mệnh, cung thân).
    """
    thang = (month - 1) % 12            # Dần = 0, Mão = 1, ...
    menh = sub(thang, hour_index)       # đếm nghịch từ giờ Tý tới giờ sinh
    than = add(thang, hour_index)       # đếm thuận từ giờ Tý tới giờ sinh
    return menh, than


def cuc_so(can_index: int, menh_cung: int) -> int:
    return CUC_TABLE[_CAN_GROUP[can_index]][_cuc_column(menh_cung)]


def tu_vi_cung(day: int, cac: int) -> int:
    """
    An sao Tử Vi: (day + k) chia hết cho cuc số, sau đó bù k cung tới/lùi.
    """
    n = cac
    k = (n - (day % n)) % n
    q = (day + k) // n
    base = add(0, q - 1)                # Dần là số 1, đếm thuận q cung.
    return add(base, k if k % 2 == 0 else -k)


def chinh_tinh(tvi: int):
    """Trả về dict tên chính tinh -> cung (cho 14 chính tinh)."""
    a = add(0, -2 * tvi)
    pos = {
        "Tử Vi": tvi,
        "Thiên Cơ": add(tvi, -1),
        "Thái Dương": add(tvi, -3),
        "Vũ Khúc": add(tvi, -4),
        "Thiên Đồng": add(tvi, -5),
        "Liêm Trinh": add(tvi, -8),
        "Thiên Phủ": add(tvi, a),
        "Thái Âm": add(tvi, a + 1),
        "Tham Lang": add(tvi, a + 2),
        "Cự Môn": add(tvi, a + 3),
        "Thiên Tướng": add(tvi, a + 4),
        "Thiên Lương": add(tvi, a + 5),
        "Thất Sát": add(tvi, a + 6),
        "Phá Quân": add(tvi, a + 10),
    }
    return pos


def cung_can_start(can_index: int) -> int:
    """Can khởi tại cung Dần (Ngũ Hổ Độn)."""
    return {0: 2, 1: 4, 2: 6, 3: 8, 4: 0, 5: 2, 6: 4, 7: 6, 8: 8, 9: 0}[can_index]


def build_chart(year_index: int, month: int, day: int, hour_index: int, gender_code: int):
    """
    year_index: 0..59 (Giáp Tý = 0).
    month: 1..12.
    day: 1..30.
    hour_index: 0=Tý .. 11=Hợi.
    gender_code: 1 = Nam, 0 = Nữ.

    Trả về dict đầy đủ các trường của một lá số.
    """
    can = _SEXAGENARY_CAN[year_index]
    chi = _SEXAGENARY_CHI_CUNG[year_index]
    can_chi_name = SEXAGENARY[year_index]
    can_name = CAN_NAMES[can]
    chi_name = CHI_NAMES_CUNG[chi]

    menh, than = cung_menh_than(month, hour_index)
    cac = cuc_so(can, menh)
    tvi = tu_vi_cung(day, cac)
    chinh = chinh_tinh(tvi)

    # Can/Chi của cung Mệnh và cung Thân.
    start_can = cung_can_start(can)
    menh_can_index = (start_can + menh) % 10
    than_can_index = (start_can + than) % 10
    can_menh = CAN_NAMES[menh_can_index]
    can_than = CAN_NAMES[than_can_index]
    can_chi_menh = f"{can_menh} {CHI_NAMES_CUNG[menh]}"
    can_chi_than = f"{can_than} {CHI_NAMES_CUNG[than]}"

    # Lai nhân cung: cung có can trùng với can năm.
    lai_nhan = next(i for i in range(12) if (start_can + i) % 10 == can)

    # Các vòng.
    duong_can = can % 2 == 0
    duong_nam = duong_can and gender_code == 1
    am_nu = (not duong_can) and gender_code == 0
    vong_thuan = ((not duong_can) and gender_code == 1) or (duong_can and gender_code == 0)
    hoa_thuan = duong_nam or am_nu

    if cac == 6:
        ts_start_thuan, ts_start_nghich = 4, 0          # Hỏa: thuận Ngọ (4), nghịch Dần (0)
    elif cac == 4:
        ts_start_thuan, ts_start_nghich = 7, 3          # Kim: thuận Dậu (7), nghịch Tỵ (3)
    elif cac == 3:
        ts_start_thuan, ts_start_nghich = 1, 9          # Mộc: thuận Mão (1), nghịch Hợi (9)
    else:                                                # Thổ, Thủy
        ts_start_thuan, ts_start_nghich = 10, 6         # thuận Tý (10), nghịch Thân (6)
    ts_start = ts_start_thuan if vong_thuan else ts_start_nghich
    if vong_thuan:
        trang_sinh = [add(ts_start, i) for i in range(12)]
    else:
        trang_sinh = [sub(ts_start, i) for i in range(12)]

    thai_tue = [add(chi, i) for i in range(12)]

    loc_ton = LOC_TON_BY_CAN[can]
    if vong_thuan:
        loc_ton_vong = [add(loc_ton, i) for i in range(13)]
    else:
        loc_ton_vong = [sub(loc_ton, i) for i in range(13)]

    # Phụ tinh theo Can.
    pos_khoi = THIEN_KHOI_BY_CAN[can]
    pos_viet = THIEN_VIET_BY_CAN[can]
    pos_duong_phu = DUONG_PHU_BY_CAN[can]
    pos_thien_quang = THIEN_QUANG_BY_CAN[can]
    pos_thien_phuc = THIEN_PHUC_BY_CAN[can]
    pos_luu_ha = LUU_HA_BY_CAN[can]
    pos_thien_tru = THIEN_TRU_BY_CAN[can]
    pos_quang_an_can = QUANG_AN_BY_CAN[can]

    # Phụ tinh theo Chi.
    pos_long_tri = LONG_TRI_BY_CHI[_chi_ord(chi)]
    pos_phuong_cac = PHUONG_CAC_BY_CHI[_chi_ord(chi)]
    pos_giai_than = GIAI_THAN_BY_CHI[_chi_ord(chi)]
    pos_thien_khoc = THIEN_KHOC_BY_CHI[_chi_ord(chi)]
    pos_thien_hu = THIEN_HU_BY_CHI[_chi_ord(chi)]
    pos_thien_duc = THIEN_DUC_BY_CHI[_chi_ord(chi)]
    pos_nguyet_duc = NGUYET_DUC_BY_CHI[_chi_ord(chi)]
    pos_hong_loan = HONG_LOAN_BY_CHI[_chi_ord(chi)]
    pos_thien_hy = THIEN_HY_BY_CHI[_chi_ord(chi)]
    pos_co_than = CO_THAN_BY_CHI[_chi_ord(chi)]
    pos_qua_tu = QUA_TU_BY_CHI[_chi_ord(chi)]
    pos_dao_hoa = DAO_HOA_BY_CHI[_chi_ord(chi)]
    pos_thien_ma = THIEN_MA_BY_CHI[_chi_ord(chi)]
    pos_kiep_sat = KIEP_SAT_BY_CHI[_chi_ord(chi)]
    pos_hoa_cai = HOA_CAI_BY_CHI[_chi_ord(chi)]
    pos_pha_toai = PHA_TOAI_BY_CHI[_chi_ord(chi)]
    pos_thien_khong = THIEN_KHONG_BY_CHI[_chi_ord(chi)]

    # Phụ tinh theo tháng.
    pos_ta_phu = TA_PHU_BY_MONTH[month - 1]
    pos_huu_bat = HUU_BAT_BY_MONTH[month - 1]
    pos_thien_hinh = THIEN_HINH_BY_MONTH[month - 1]
    pos_thien_dieu = THIEN_DIEU_BY_MONTH[month - 1]
    pos_thien_y = THIEN_Y_BY_MONTH[month - 1]
    pos_thien_giai = THIEN_GIAI_BY_MONTH[month - 1]
    pos_dia_giai = DIA_GIAI_BY_MONTH[month - 1]

    # Phụ tinh theo giờ.
    pos_van_xuong = VAN_XUONG_BY_HOUR[hour_index]
    pos_van_khuc = VAN_KHUC_BY_HOUR[hour_index]
    pos_thai_phu = THAI_PHU_BY_HOUR[hour_index]
    pos_phong_cao = PHONG_CAO_BY_HOUR[hour_index]
    pos_dia_khong = DIA_KHONG_BY_HOUR[hour_index]
    pos_dia_kiep = DIA_KIEP_BY_HOUR[hour_index]

    # Hỏa / Linh.
    for (_group, (hoa_start, linh_start)) in HOA_LINH_KHOI.items():
        if chi in _group:
            break
    if hoa_thuan:
        pos_hoa_tinh = add(hoa_start, hour_index)
        pos_linh_tinh = sub(linh_start, hour_index)
    else:
        pos_hoa_tinh = sub(hoa_start, hour_index)
        pos_linh_tinh = add(linh_start, hour_index)

    # Tam Thai / Bát Tọa / Ân Quang / Thiên Quý.
    pos_tam_thai = add(pos_ta_phu, day - 1)
    pos_bat_toa = sub(pos_huu_bat, day - 1)
    pos_an_quang = add(pos_van_xuong, day - 2)
    pos_thien_quy = add(pos_van_khuc, -(day - 2))

    # Tuần / Triệt.
    pos_tuan = TUAN_BY_TUAN[year_index // 10]
    triet_1, triet_2 = TRIET_BY_CAN[can]

    # Sao mang tính "cố định" trên địa bàn.
    pos_thien_la = 2                       # Thìn
    pos_dia_vong = 8                       # Tuất
    # Theo thứ tự cung thuận từ Mệnh: Mệnh(0), Phụ Mẫu(1), Phúc Đức(2),
    # Điền Trạch(3), Quan Lộc(4), Nô Bộc(5), Thiên Di(6), Tật Ách(7), ...
    pos_thien_thuong = add(menh, 5)        # Nô Bộc
    pos_thien_su = add(menh, 7)            # Tật Ách
    pos_dau_quan = add(add(chi, hour_index), -(month - 1))
    pos_thien_tai = add(menh, chi)
    pos_thien_tho = add(than, chi)

    # Tập vị trí để tra Tứ Hoá.
    pos_map = dict(chinh)
    pos_map.update({
        "Văn Xương": pos_van_xuong,
        "Văn Khúc": pos_van_khuc,
        "Tả Phù": pos_ta_phu,
        "Hữu Bật": pos_huu_bat,
        "Nguyệt Đức": pos_nguyet_duc,
    })

    hoa_loc_sao = HOA_LOC_BY_CAN[can]
    hoa_quyen_sao = HOA_QUYEN_BY_CAN[can]
    hoa_khoa_sao = HOA_KHOA_BY_CAN[can]
    hoa_ky_sao = HOA_KY_BY_CAN[can]
    pos_hoa_loc = pos_map[hoa_loc_sao]
    pos_hoa_quyen = pos_map[hoa_quyen_sao]
    pos_hoa_khoa = pos_map[hoa_khoa_sao]
    pos_hoa_ky = pos_map[hoa_ky_sao]

    row = {
        "year_index": year_index,
        "year_can_chi": can_chi_name,
        "year_can": can_name,
        "year_can_index": can,
        "year_chi": chi_name,
        "year_chi_index": chi,
        "lunar_month": month,
        "lunar_day": day,
        "hour_index": hour_index,
        "hour_label": HOUR_NAMES[hour_index],
        "gender_code": gender_code,
        "gender_label": "Nam" if gender_code == 1 else "Nữ",
        "duong_nam": int(duong_nam),
        "am_nu": int(am_nu),
        "vong_thuan": int(vong_thuan),
        "hoa_thuan": int(hoa_thuan),
        "menh_cung": menh,
        "menh_cung_label": cung_label(menh, menh),
        "than_cung": than,
        "than_cung_label": cung_label(than, menh),
        "cuc_so": cac,
        "cuc_hanh": CUC_HANH[cac],
        "cuc": CUC_NAMES[cac],
        "menh_can_index": menh_can_index,
        "than_can_index": than_can_index,
        "menh_chi_index": menh,
        "than_chi_index": than,
        "can_chi_menh": can_chi_menh,
        "can_chi_than": can_chi_than,
        "lai_nhan_cung": lai_nhan,
        "tu_vi_cung": tvi,
    }
    # 14 chính tinh.
    for name in CHINH_TINH_NAMES:
        row[f"pos_{star_key(name)}"] = chinh[name]

    # Vòng Trường Sinh.
    for name, pos in zip(TRANG_SINH_NAMES, trang_sinh):
        row[f"pos_{star_key(name)}"] = pos

    # Vòng Thái Tuế.
    for name, pos in zip(THAI_TUE_NAMES, thai_tue):
        row[f"pos_{star_key(name)}"] = pos

    # Vòng Lộc Tồn.
    for name, pos in zip(LOC_TON_NAMES, loc_ton_vong):
        row[f"pos_{star_key(name)}"] = pos

    # Phụ tinh theo Can.
    row.update({
        "pos_thien_quang": pos_thien_quang,
        "pos_thien_phuc": pos_thien_phuc,
        "pos_luu_ha": pos_luu_ha,
        "pos_thien_tru": pos_thien_tru,
        "pos_quang_an_can": pos_quang_an_can,
        "pos_kinh_duong": KINH_DUONG_BY_CAN[can],
        "pos_da_la": DA_LA_BY_CAN[can],
        "pos_thien_khoi": pos_khoi,
        "pos_thien_viet": pos_viet,
    })

    # Phụ tinh theo Chi.
    row.update({
        "pos_long_tri": pos_long_tri,
        "pos_phuong_cac": pos_phuong_cac,
        "pos_giai_than": pos_giai_than,
        "pos_thien_khoc": pos_thien_khoc,
        "pos_thien_hu": pos_thien_hu,
        "pos_thien_duc": pos_thien_duc,
        "pos_nguyet_duc": pos_nguyet_duc,
        "pos_hong_loan": pos_hong_loan,
        "pos_thien_hy": pos_thien_hy,
        "pos_co_than": pos_co_than,
        "pos_qua_tu": pos_qua_tu,
        "pos_dao_hoa": pos_dao_hoa,
        "pos_thien_ma": pos_thien_ma,
        "pos_kiep_sat": pos_kiep_sat,
        "pos_hoa_cai": pos_hoa_cai,
        "pos_pha_toai": pos_pha_toai,
        "pos_thien_khong": pos_thien_khong,
    })

    # Phụ tinh theo tháng.
    row.update({
        "pos_ta_phu": pos_ta_phu,
        "pos_huu_bat": pos_huu_bat,
        "pos_thien_hinh": pos_thien_hinh,
        "pos_thien_dieu": pos_thien_dieu,
        "pos_thien_y": pos_thien_y,
        "pos_thien_giai": pos_thien_giai,
        "pos_dia_giai": pos_dia_giai,
    })

    # Phụ tinh theo giờ.
    row.update({
        "pos_van_xuong": pos_van_xuong,
        "pos_van_khuc": pos_van_khuc,
        "pos_thai_phu": pos_thai_phu,
        "pos_phong_cao": pos_phong_cao,
        "pos_dia_khong": pos_dia_khong,
        "pos_dia_kiep": pos_dia_kiep,
    })

    # Hỏa Linh, Thai Toạ, Quang Quý, Tuần Triệt, cố định, Tứ Hoá.
    row.update({
        "pos_hoa_tinh": pos_hoa_tinh,
        "pos_linh_tinh": pos_linh_tinh,
        "pos_tam_thai": pos_tam_thai,
        "pos_bat_toa": pos_bat_toa,
        "pos_an_quang": pos_an_quang,
        "pos_thien_quy": pos_thien_quy,
        "pos_tuan": pos_tuan,
        "pos_triet_1": triet_1,
        "pos_triet_2": triet_2,
        "pos_thien_la": pos_thien_la,
        "pos_dia_vong": pos_dia_vong,
        "pos_thien_thuong": pos_thien_thuong,
        "pos_thien_su": pos_thien_su,
        "pos_dau_quan": pos_dau_quan,
        "pos_thien_tai": pos_thien_tai,
        "pos_thien_tho": pos_thien_tho,
        "hoa_loc_sao": hoa_loc_sao,
        "pos_hoa_loc": pos_hoa_loc,
        "hoa_quyen_sao": hoa_quyen_sao,
        "pos_hoa_quyen": pos_hoa_quyen,
        "hoa_khoa_sao": hoa_khoa_sao,
        "pos_hoa_khoa": pos_hoa_khoa,
        "hoa_ky_sao": hoa_ky_sao,
        "pos_hoa_ky": pos_hoa_ky,
    })

    # Nhóm để truy xuất nhanh.
    row["group_cuc"] = row["cuc"]
    row["group_cuc_so"] = cac
    row["group_tu_vi"] = CHI_NAMES_CUNG[tvi]
    row["group_menh"] = CHI_NAMES_CUNG[menh]
    row["group_than"] = CHI_NAMES_CUNG[than]
    row["group_nam"] = can_chi_name
    row["group_thang"] = month
    row["group_gio"] = HOUR_NAMES[hour_index]
    row["group_gioi_tinh"] = row["gender_label"]
    # Một số tổ hợp nhóm dễ dùng.
    row["group_cuc_tu_vi"] = f"{row['cuc']}|{row['group_tu_vi']}"
    row["group_can_chi_cuc"] = f"{can_chi_name}|{row['cuc']}"
    # Tên 12 cung (theo vị trí địa chỉ), dùng khi muốn lập bảng 12 cung.
    for pos in range(12):
        row[f"cung_label_{pos}"] = cung_label(pos, menh)
    return row


def _chi_ord(chi_index: int) -> int:
    """Chuyển chỉ số cung (Dần=0..Sửu=11) sang thứ tự Tý=0..Hợi=11."""
    return (chi_index + 2) % 12
