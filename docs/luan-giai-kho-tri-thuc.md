# Kho tri thức luận giải (giống AI)

Đây là tầng thứ ba của kho dữ liệu, bên trên:

1. **Kho lá số**: 518.400 chart (SQLite + CSV partition).
2. **Kho sao-cung**: 109 sao × 12 cung = 1.308 mô tả.
3. **Kho tri thức luận giải**: hồ sơ chuyên sâu theo lĩnh vực + cách cục + quy tắc luận.

## Nội dung kho

### Bảng `main_star_profile` (14 chính tinh)

Mỗi chính tinh còn chứa thêm:

- `element`, `nature` (cát / cát-hung), `about`
- `tinh_cach`, `su_nghiep`, `tai_loc`, `tinh_duyen`, `suc_khoe`
- `note` (lưu ý khi luận)

### Bảng `cung_profile` (12 cung)

Mỗi cung có: tên cung (`cung_name`), phạm vi (`domain`), mặt tích cực
(`positive`), hạn chế (`negative`), khuyến nghị (`advice`).

### Bảng `cuc_profile` (5 cục)

Mỗi cục có: hành, bản chất, sự nghiệp, tài lộc, tình duyên, lưu ý.

### Bảng `tua_hoa_profile` (4 trường hợp Tứ Hoá)

Mô tả Hóa Lộc / Quyền / Khoa / Kỵ.

### Bảng `cach_rules` (16 + 8 quy tắc)

- 16 cách cục đặc trưng (Tử Vi thủ Mệnh, Thân cư Mệnh, Lộc Tồn tại Tài,
  Văn Xương/Khúc tại Mệnh, Khôi Việt tại Mệnh, Hóa Lộc/Quyền/Kỵ tại Mệnh,
  Hỏa/Linh tại Mệnh, Đào Hoa tại Phu Thê, Vũ Tham đồng cung, ...).
- 8 quy tắc luận tổng hợp.

### Bảng `star_cung_analysis` (1.308 dòng) — luận khách quan 3 chiều

Mỗi sao × mỗi cung đều có:

- `ban_chat` : bản chất, trung tính.
- `positive` : mặt tích cực thật.
- `negative` : mặt hạn chế / tiêu cực thật (không nói giảm, không nói tránh).
- `comparison` : đánh giá cân bằng.

14 chính tinh có nội dung viết tay cho đủ 168 tổ hợp (14 × 12). Các phụ tinh
được sinh từ ẩn nghĩa sao + tính chất cung.

## Cách build

```bash
python3 scripts/build_luan_giai_knowledge.py
```

Ghi ra:

- `data/luan_giai/luan_giai_knowledge.json`
- các bảng `main_star_profile`, `cung_profile`, `cuc_profile`,
  `tua_hoa_profile`, `cach_rules` trong `data/tuvi_518400.sqlite`.

## Sinh bài luận giải tự động

```bash
python3 scripts/luan_giai_chart.py --chart-id 106920 --format markdown
python3 scripts/luan_giai_chart.py --chart-id 106920 --format text
python3 scripts/luan_giai_chart.py --chart-id 106920 --format json
```

Các phần trong bài luận giải:

1. **Thông tin lá số** — năm/tháng/ngày/giờ, giới tính, Mệnh/Thân, Cục, Tử Vi.
2. **Mệnh và Thân** — sao chính thủ Mệnh, thủ Thân, Thân cư Mệnh/Quan Lộc.
3. **Phân tích 12 cung** — cung có chính tinh thủ, kèm chú giải theo lĩnh vực.
4. **Tứ Hoá** — nêu Lộc/Quyền/Khoa/Kỵ.
5. **Cách cục nổi bật** — các "cách" được phát hiện tự động.
6. **Bản chất, ưu điểm và hạn chế/tiêu cực** — phân tích khách quan từng sao nổi bật,
   nói thẳng mặt yếu (dựa trên bảng `star_cung_analysis`).
7. **Gợi ý cuộc sống** — khuyến nghị dựa trên lá số.

## Truy vấn trực tiếp

```sql
-- Hồ sơ Tử Vi
SELECT * FROM main_star_profile WHERE star_name = 'Tử Vi';

-- Cách cục
SELECT * FROM cach_rules WHERE muc = 'cat_cach';

-- Nhìn nhanh một chart + tên cung của Tử Vi
SELECT c.chart_id, c.pos_tu_vi, c.menh_cung, s.star_name, s.cung_name, s.description
FROM charts c
JOIN star_cung_knowledge s
  ON s.star_key = 'tu_vi'
 AND s.cung_index = (c.pos_tu_vi - c.menh_cung + 12) % 12
WHERE c.chart_id = 106920;
```

## Ví dụ kết quả

File `docs/luan-giai-106920.md` là bài luận giải đầy đủ cho chart 106920
(Nam, Bính Tý, tháng 10, ngày 1, giờ Tý).
