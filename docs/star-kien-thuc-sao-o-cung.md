# Kho kiến thức "Sao ở Cung"

## Dữ liệu là gì?

Bảng kiến thức mô tả **ý nghĩa của từng sao khi đóng tại từng cung**. Hiện có
**1.308 dòng** = 109 sao × 12 cung, bao gồm:

- 14 chính tinh × 12 cung (mô tả riêng, đầy đủ).
- Các phụ tinh, vòng Trường Sinh, Thái Tuế, Lộc Tồn, Tứ Hoá, Hỏa Linh, Quang Quý…
  × 12 cung (mô tả tổng hợp từ ẩn nghĩa sao + tính chất cung).

Mỗi dòng gồm: `star_key`, `star_name`, `star_group`, `nature` (tốt/xấu/trung),
`cung_index`, `cung_name`, `description`, `keywords`.

## Cung index như thế nào?

`cung_index` là **vị trí tương đối so với cung Mệnh** (0..11):

| index | Cung | | index | Cung |
|---|---|---|---|---|
| 0 | Mệnh | | 6 | Thiên Di |
| 1 | Phụ Mẫu | | 7 | Tật Ách |
| 2 | Phúc Đức | | 8 | Tài Bạch |
| 3 | Điền Trạch | | 9 | Tử Tức |
| 4 | Quan Lộc | | 10 | Phu Thê |
| 5 | Nô Bộc | | 11 | Huynh Đệ |

Đối với một lá số (chart), cung của một sao là:

```
cung_index = (pos_star - menh_cung) % 12
```

trong đó `pos_star` và `menh_cung` nằm trong bảng `charts` (chỉ số 0=Dần..11=Sửu).

## Các file sinh ra

Chạy `python3 scripts/build_star_knowledge.py` để tạo:

- `data/star_knowledge/star_cung_knowledge.json` — mỗi dòng 1 đối tượng.
- `data/star_knowledge/star_cung_knowledge.csv.gz` — bảng CSV nén.
- Bảng `star_cung_knowledge` trong `data/tuvi_518400.sqlite`.

## Truy vấn

### 1. Một sao × 12 cung

```bash
python3 scripts/query_star_knowledge.py --star tu_vi
python3 scripts/query_star_knowledge.py --star loc_ton
```

### 2. Một cung × tất cả sao

```bash
python3 scripts/query_star_knowledge.py --cung 6     # Thiên Di
```

### 3. Ghép với một lá số cụ thể trong kho 518.400

```bash
python3 scripts/query_star_knowledge.py --chart-id 106920
python3 scripts/query_star_knowledge.py --chart-id 106920 --format md
```

Câu SQL tương đương để tự động hoá:

```sql
SELECT s.star_name, s.cung_name, s.description
FROM charts c
JOIN star_cung_knowledge s
  ON s.star_key = 'tu_vi'
 AND s.cung_index = (c.pos_tu_vi - c.menh_cung + 12) % 12
WHERE c.chart_id = 106920;
```

## Tạo mới / mở rộng nội dung

Nguồn nội dung nằm trong `scripts/star_knowledge_data.py`:

- `STAR_META` : ẩn nghĩa gốc của từng sao.
- `DETAIL_MAIN` : 14 chính tinh × 12 cung (mô tả riêng).
- `DETAIL_EXTRA` : thêm mô tả riêng cho phụ tinh (tuỳ chọn).

Muốn thêm/bổ sung sao hoặc viết lại câu chữ cho một sao-cung, sửa file rồi chạy lại
`python3 scripts/build_star_knowledge.py` (không cần tái tạo lại cả kho 518.400 lá số).

## Ví dụ kết quả cho lá số 106920

Xem `docs/tuvi-106920-sao-o-cung.md` — bản markdown đầy đủ **sao ở 12 cung**
của lá số Bính Tý / tháng 10 / ngày 1 / giờ Tý, nam.
