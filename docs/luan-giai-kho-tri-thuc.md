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

### Tầng `luan_giai_integrated` — luận giải LIÊN KẾT (chính tinh + phụ tinh)

Đây là lớp đọc "liền mạch" phía trên kho tri thức:

- Gom **tất cả sao đóng trong cùng một cung** (chính tinh, phụ tinh, bộ sao
  vòng Trường Sinh / vòng Thái Tuế / vòng Lộc Tồn) thành một khối duy nhất.
- Thay vì liệt kê từng sao rời rạc, mỗi cung có:
  - **Bản chất liên kết** — chính tinh định hình cung, phụ tinh làm mạnh/yếu;
  - **Điểm mạnh** — gộp mặt tích cực của chính tinh + phụ tinh tốt;
  - **Điểm yếu / cần lưu ý** — gộp mặt hạn chế của chính tinh + phụ tinh xấu;
  - **Gợi ý cho cung**.
- **Tổng quan liên kết** ở đầu bài nối Mệnh – Thân – Tứ Hoá – trục Quan Lộc /
  Tài Bạch / Phu Thê.

### Bảng `star_combo_analysis` — tổ hợp / biến thể sao (hơn 100 dòng)

Khác với `star_cung_analysis` (một sao ở một cung), bảng này mô tả khi **hai sao
gặp nhau** trong cùng lá số: cùng cung, tam hợp hoặc xung chiếu.

Mỗi tổ hợp có:

- `ban_chat` : bản chất thật của tổ hợp (trung tính).
- `positive` : mặt tích cực rõ, có cơ sở.
- `negative` : mặt hạn chế / tiêu cực rõ, không nói giảm, không nói tránh.
- `note`     : điều kiện đắc/hãm, cung đóng làm tổ hợp mạnh/yếu.
- `category` : loại tổ hợp (quyền-tài, tài-dục, tăng-lực, đào-hoa, ...).
- `source`   : `authored` (viết tay) hay `synth` (sinh từ hồ sơ hai sao).

Kho có:

- **40+ tổ hợp viết tay**: Tử Phủ, Phủ Tướng, Vũ Tham, Tử Tham, Tử Sát, Tử Phá,
  Nhật Nguyệt, Cơ Lương, Đồng Âm, Đồng Cự, Nhật Cự, Nhật Lương, Liêm Sát,
  Lộc/Kình/Đà/Hỏa/Linh/Văn Xương/Khúc/Khôi/Việt/Đào/Hoa-Lộc/Hóa-Kỵ, ...
- **67 cặp sinh tự động** bổ sung đủ 91 cặp 14 chính tinh để kho không bị thiếu
  cặp nào khi tra cứu.

## Cách build

```bash
python3 scripts/build_luan_giai_knowledge.py
python3 scripts/build_star_combo.py
```

Ghi ra:

- `data/luan_giai/luan_giai_knowledge.json`
- `data/luan_giai/star_cung_analysis.json`
- `data/luan_giai/star_combo_analysis.json`
- các bảng `main_star_profile`, `cung_profile`, `cuc_profile`,
  `tua_hoa_profile`, `cach_rules`, `star_cung_analysis`, `star_combo_analysis`
  trong `data/tuvi_518400.sqlite`.

## Sinh bài luận giải tự động

```bash
python3 scripts/luan_giai_chart.py --chart-id 106920 --format markdown
python3 scripts/luan_giai_chart.py --chart-id 106920 --format text
python3 scripts/luan_giai_chart.py --chart-id 106920 --format json
```

Các phần trong bài luận giải:

1. **Thông tin lá số** — năm/tháng/ngày/giờ, giới tính, Mệnh/Thân, Cục, Tử Vi.
2. **Tổng quan liên kết** — nối Mệnh – Thân – trục Quan Lộc / Tài Bạch / Phu Thê.
3. **Mệnh và Thân (liên kết)** — chính tinh + phụ tinh + bộ sao tại Mệnh/Thân.
4. **Phân tích 12 cung (liên kết)** — mỗi cung một đoạn Bản chất liên kết /
   Điểm mạnh / Điểm yếu, gộp chính tinh + phụ tinh + bộ sao.
5. **Tứ Hoá** — nêu Lộc/Quyền/Khoa/Kỵ.
6. **Cách cục nổi bật** — các "cách" được phát hiện tự động.
7. **Bản chất, ưu điểm và hạn chế/tiêu cực (chi tiết từng sao)** — phân tích
   khách quan từng sao nổi bật, nói thẳng mặt yếu (bảng `star_cung_analysis`).
8. **Tổ hợp sao nổi bật** — nêu các cặp sao thực sự gặp nhau (cùng cung / tam hợp /
   xung chiếu) hoặc thuộc nhóm tổ hợp nổi tiếng; mỗi cặp trình bày
   Bản chất / Tích cực / Tiêu cực / Lưu ý (bảng `star_combo_analysis`).
9. **Gợi ý cuộc sống** — khuyến nghị dựa trên lá số.

## Truy xuất kho tổ hợp sao

```bash
# Xem một tổ hợp
python3 scripts/query_star_combo.py --combo tu_vi thien_phu

# Tìm kiếm
python3 scripts/query_star_combo.py --search "Đào Hoa"

# Liệt kê toàn bộ
python3 scripts/query_star_combo.py --list
```

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
