# Ví dụ truy vấn kho 518.400 lá số Tử Vi

## 1. Tổng số lá số

```sql
SELECT COUNT(*) FROM charts;
-- 518400
```

```bash
python3 scripts/query_warehouse.py --run "SELECT COUNT(*) FROM charts"
```

## 2. Đếm theo từng nhóm (Group By)

```sql
SELECT cuc_so, COUNT(*) AS so_la_so
FROM charts
GROUP BY cuc_so
ORDER BY cuc_so;
```

```bash
python3 scripts/query_warehouse.py --group cuc_so
```

### Đếm theo vị trí Tử Vi

```sql
SELECT tu_vi_cung, COUNT(*)
FROM charts
GROUP BY tu_vi_cung
ORDER BY tu_vi_cung;
```

### Đếm theo năm Can-Chi

Vì bảng `charts` chỉ lưu `year_index` (0..59), tra tên bằng
`data/metadata/dimensions.json`:

```python
import sqlite3, json

dims = json.load(open("data/metadata/dimensions.json", encoding="utf-8"))
conn = sqlite3.connect("data/tuvi_518400.sqlite")

for y, count in conn.execute(
    "SELECT year_index, COUNT(*) FROM charts GROUP BY year_index ORDER BY year_index"
):
    print(dims["sexagenary"][y], count)
```

## 3. Tìm một nhóm lá số cụ thể

Ví dụ **nam, Hỏa Lục Cục, Tử Vi tại Dậu** (Dậu = chỉ số 7):

```sql
SELECT year_index, gender_code, lunar_month, lunar_day, hour_index,
       cuc_so, tu_vi_cung, menh_cung, than_cung
FROM charts
WHERE gender_code = 1
  AND cuc_so = 6
  AND tu_vi_cung = 7
LIMIT 10;
```

## 4. Truy vấn chính tinh trong SQLite

Bảng `charts` đã chứa 14 chính tinh. Ví dụ **lọc Mệnh tại Dần (0), sao Tử Vi
tại Thìn (2)**:

```sql
SELECT chart_id, year_index, gender_code, cuc_so,
       pos_tu_vi, pos_thien_co, pos_thai_duong, pos_vu_khuc,
       pos_thien_dong, pos_liem_trinh, pos_thien_phu, pos_thai_am,
       pos_tham_lang, pos_cu_mon, pos_thien_tuong, pos_thien_luong,
       pos_that_sat, pos_pha_quan
FROM charts
WHERE menh_cung = 0 AND pos_tu_vi = 2
LIMIT 20;
```

## 5. Truy xuất toàn bộ chi tiết từ CSV partition

Mỗi Cục có một file `data/csv_by_cuc/tuvi_by_cuc_{cuc_so}.csv.gz`. File này
chứa **toàn bộ cột sao** (không chỉ 14 chính tinh).

Ví dụ đọc Cục 6 bằng `pandas` (nếu có):

```python
import gzip, pandas as pd

df = pd.read_csv("data/csv_by_cuc/tuvi_by_cuc_6.csv.gz")
print(df.shape)                       # (103680, 144)
print(df[df["pos_thien_co"] == 0].head())
```

Nếu không dùng `pandas`, có thể đọc bằng thư viện chuẩn:

```python
import gzip, csv, json

with gzip.open("data/csv_by_cuc/tuvi_by_cuc_6.csv.gz", "rt") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        print(json.dumps(row, ensure_ascii=False))
        if i >= 4:
            break
```

## 6. Tìm nhóm có sao Hóa Lộc tại một cung

Cột `pos_hoa_loc` chỉ có trong CSV full-detail (không có trong SQLite compact).

```python
import gzip, csv

rows = []
with gzip.open("data/csv_by_cuc/tuvi_by_cuc_6.csv.gz", "rt") as f:
    for r in csv.DictReader(f):
        if r["pos_hoa_loc"] == "4":     # Ngọ
            rows.append(r)
print(len(rows), "lá số")
```

## 7. Khớp nhãn tên khi cần

Vị trí cung được lưu bằng số 0..11 theo bảng:

```
0 Dần, 1 Mão, 2 Thìn, 3 Tỵ, 4 Ngọ, 5 Mùi,
6 Thân, 7 Dậu, 8 Tuất, 9 Hợi, 10 Tý, 11 Sửu
```

Giờ `hour_index`: `0 Tý, 1 Sửu, 2 Dần, 3 Mão, 4 Thìn, 5 Tỵ, 6 Ngọ, 7 Mùi,
8 Thân, 9 Dậu, 10 Tuất, 11 Hợi`.

Bảng tra có trong `data/metadata/dimensions.json`:

```python
import json
d = json.load(open("data/metadata/dimensions.json", encoding="utf-8"))
print(d["chi_cung_names"])   # tên cung theo chỉ số
print(d["sexagenary"])       # 60 hoa giáp
```
