# Kho dữ liệu 518.400 biến thể lá số Tử Vi

Kho dữ liệu sinh đủ **60 năm Can-Chi × 2 giới tính × 12 tháng × 12 giờ × 30 ngày
= 518.400 lá số Tử Vi**, mỗi lá số được "an sao" theo thuật toán Bắc phái phổ biến
tại Việt Nam (nguồn và các lựa chọn trường phái được ghi trong
[docs/nguon-algorithm.md](docs/nguon-algorithm.md)).

## Cấu trúc kho

```
tuvi-off/
├── README.md                         # Tổng quan này
├── .gitignore                        # Dữ liệu sinh ra không đẩy lên Git
├── scripts/
│   ├── tuvi_engine.py                # Engine an sao (thuần Python)
│   ├── generate_warehouse.py         # Sinh 518.400 lá số + kho SQLite + CSV partition
│   └── query_warehouse.py            # Công cụ truy xuất kho
├── docs/
│   ├── nguon-algorithm.md            # Thuật toán, nguồn, trường phái
│   ├── schema.md                     # Schema cột
│   └── query-vi-du.md                # Câu truy vấn mẫu
└── data/                             # Được tạo bằng generator (gitignored)
    ├── tuvi_518400.sqlite            # Kho chính (compact index)
    ├── csv_by_cuc/
    │   ├── tuvi_by_cuc_2.csv.gz
    │   ├── tuvi_by_cuc_3.csv.gz
    │   ├── tuvi_by_cuc_4.csv.gz
    │   ├── tuvi_by_cuc_5.csv.gz
    │   └── tuvi_by_cuc_6.csv.gz      # 5 partition đầy đủ chi tiết theo Cục
    ├── json_sample/tuvi_sample_5.json
    └── metadata/
        ├── groups.json               # Số lượng theo từng nhóm
        ├── dimensions.json           # Bảng tra Can, Chi, Cục, 60 hoa giáp, ...
        └── manifest.json             # SHA-256 + số byte của từng partition
```

## Tạo lại kho

```bash
# Toàn bộ 518.400 lá số (~40 giây trên máy chạy được).
python3 scripts/generate_warehouse.py

# Thử nhanh với 1000 dòng.
python3 scripts/generate_warehouse.py --limit 1000
```

## Truy xuất kho

```bash
# Tổng quan + đếm nhóm Cục và vị trí Tử Vi.
python3 scripts/query_warehouse.py

# Đếm theo một nhóm.
python3 scripts/query_warehouse.py --group cuc_so
python3 scripts/query_warehouse.py --group tu_vi_cung

# Câu SQL tuỳ ý.
python3 scripts/query_warehouse.py --run \
  "SELECT * FROM charts WHERE cuc_so=6 AND gender_code=1 LIMIT 10"

# Đọc chi tiết đầy đủ của một partition (Cục 6) dưới dạng JSON.
python3 scripts/query_warehouse.py --detail-group 6 --limit 5
```

Hoặc dùng trực tiếp SQLite / pandas / DuckDB:

```python
import sqlite3, gzip, csv

conn = sqlite3.connect("data/tuvi_518400.sqlite")
for row in conn.execute(
    "SELECT count(*) FROM charts WHERE cuc_so = 6 AND tu_vi_cung = 7"
):
    print(row)
```

## Nhóm dữ liệu chính

| Nhóm | Cột trong SQLite / CSV | Số nhóm |
|------|------------------------|---------|
| Ngũ Hành Cục | `cuc_so` | 5 |
| Vị trí Tử Vi | `tu_vi_cung` | 12 |
| Cung Mệnh | `menh_cung` | 12 |
| Cung Thân | `than_cung` | 12 |
| Tên 12 cung | `cung_label_0..11` | lưu trong CSV full-detail |
| Năm Can-Chi | `year_index` | 60 |
| Tháng / Giờ / Giới tính | `lunar_month`, `hour_index`, `gender_code` | 12 / 12 / 2 |

Ngoài ra trong CSV nén còn đầy đủ 14 chính tinh + các phụ tinh (140+ cột sao,
xem [docs/schema.md](docs/schema.md) và [docs/query-vi-du.md](docs/query-vi-du.md)).

## Lưu ý

- Dữ liệu dựa trên **lịch âm** (tháng 1..12, ngày 1..30) và **60 hoa giáp**,
  không bao gồm bước đổi lịch Dương → Âm hay tháng nhuận (xem
  [nguon-algorithm.md](docs/nguon-algorithm.md)).
- Có một số trường phái an Hỏa/Linh Tinh cho nhóm Tỵ-Dậu-Sửu; kho dữ liệu dùng
  **Hỏa khởi Mão, Linh khởi Tuất** (trường phái Bắc phái thông dụng).
- Toàn bộ file dữ liệu sinh ra được `.gitignore`; scripts và docs được lưu trong Git.
